"""
AI Study Assistant — Backend API
Module 2: PYQ Priority Prediction + Historical Question Analysis

Loads exactly two artifacts (confirmed from the uploaded files):
  models/study_assistant_model.pkl  -> sklearn LinearSVC, classes_ = ['High','Low','Medium']
  models/tfidf_vectorizer.pkl       -> sklearn TfidfVectorizer
                                        (ngram_range=(1,2), lowercase=True,
                                         stop_words='english' — it already
                                         handles lowercasing/tokenizing/stopwords,
                                         so raw text is passed straight in,
                                         no manual cleaning needed)

Notes on this specific model:
  - No label_encoder.pkl — the model predicts 'High'/'Low'/'Medium' directly.
  - LinearSVC has no predict_proba, only decision_function, so "confidence"
    below is a softmax over the decision margins (a reasonable proxy, not a
    calibrated probability).

Also loads DATASET/dataset/<subject>/pyq.csv for historical lookups
(times repeated / papers / marks). Adjust PYQ_DATA_DIR if that's wrong.

Run locally:
    pip install -r requirements.txt
    python app.py

Deploy on Vercel:
    { "builds": [{ "src": "api/app.py", "use": "@vercel/python" }],
      "routes": [{ "src": "/(.*)", "dest": "api/app.py" }] }
"""

import os
import re
import csv
import glob
import pickle
import traceback

import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
PYQ_DATA_DIR = os.path.join(BASE_DIR, "..", "DATASET", "dataset")  # ADJUST IF NEEDED

# ---------------------------------------------------------------------------
# Load ML model artifacts once at startup
# ---------------------------------------------------------------------------
def load_pickle(filename):
    with open(os.path.join(MODELS_DIR, filename), "rb") as f:
        return pickle.load(f)


try:
    model = load_pickle("study_assistant_model.pkl")
    vectorizer = load_pickle("tfidf_vectorizer.pkl")
    MODEL_LOAD_ERROR = None
except Exception as e:
    model = vectorizer = None
    MODEL_LOAD_ERROR = str(e)


def ml_predict_priority(question_text: str):
    """
    Fallback prediction when no historical PYQ match is found.
    The vectorizer already lowercases/tokenizes/strips stop words, so we
    pass the raw question straight in.
    """
    features = vectorizer.transform([question_text])
    priority = model.predict(features)[0]  # e.g. 'High' — no decoding needed

    result = {"priority": str(priority), "source": "ml_prediction"}

    # LinearSVC has no predict_proba — approximate confidence via softmax
    # over the decision-function margins instead.
    if hasattr(model, "decision_function"):
        scores = model.decision_function(features)[0]
        exp_scores = np.exp(scores - np.max(scores))
        softmax = exp_scores / exp_scores.sum()
        class_confidences = {
            str(cls): round(float(p), 4) for cls, p in zip(model.classes_, softmax)
        }
        result["confidence"] = round(float(max(softmax)), 4)
        result["class_confidences"] = class_confidences

    return result


# ---------------------------------------------------------------------------
# Load PYQ historical data (repeats / papers / marks) for every subject
# ---------------------------------------------------------------------------
PYQ_INDEX = []
PYQ_LOAD_ERRORS = []


def parse_count(count_str):
    """'6/7' -> (6, 7). Falls back to (0, 1) if malformed."""
    try:
        num, denom = count_str.strip().split("/")
        return int(num), int(denom)
    except Exception:
        return 0, 1


def derive_priority(times, total):
    if total == 0:
        return "Low"
    ratio = times / total
    if ratio >= 0.6:
        return "High"
    elif ratio >= 0.3:
        return "Medium"
    return "Low"


def load_pyq_data():
    if not os.path.isdir(PYQ_DATA_DIR):
        PYQ_LOAD_ERRORS.append(f"PYQ data dir not found: {PYQ_DATA_DIR}")
        return

    csv_paths = glob.glob(os.path.join(PYQ_DATA_DIR, "*", "pyq.csv"))
    for path in csv_paths:
        subject = os.path.basename(os.path.dirname(path))
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    topic = (row.get("Topic_Name") or "").strip()
                    if not topic:
                        continue
                    times, total = parse_count(row.get("Count", "0/1"))
                    papers = [p.strip() for p in (row.get("Papers") or "").split(",") if p.strip()]
                    marks = [m.strip() for m in (row.get("Marks") or "").split(",") if m.strip()]
                    keywords = set(re.findall(r"\b\w{3,}\b", topic.lower()))

                    PYQ_INDEX.append({
                        "subject": subject,
                        "section": (row.get("Section") or "").strip(),
                        "topic": topic,
                        "times_repeated": times,
                        "total_papers": total,
                        "papers": papers,
                        "marks": marks,
                        "priority": derive_priority(times, total),
                        "keywords": keywords,
                    })
        except Exception as e:
            PYQ_LOAD_ERRORS.append(f"Failed to load {path}: {e}")


load_pyq_data()


def match_question_to_pyq(question_text: str, min_score: float = 1.5):
    q_words = set(re.findall(r"\b\w{3,}\b", question_text.lower()))
    if not q_words:
        return None

    best_entry, best_score = None, 0.0
    for entry in PYQ_INDEX:
        overlap = len(q_words & entry["keywords"])
        if overlap == 0:
            continue
        ratio = entry["times_repeated"] / entry["total_papers"] if entry["total_papers"] else 0
        score = overlap + ratio
        if score > best_score:
            best_score, best_entry = score, entry

    if best_entry and best_score >= min_score:
        return best_entry
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok" if not MODEL_LOAD_ERROR else "error",
        "model_error": MODEL_LOAD_ERROR,
        "model_classes": list(model.classes_) if model is not None else None,
        "pyq_topics_loaded": len(PYQ_INDEX),
        "pyq_load_errors": PYQ_LOAD_ERRORS,
    }), (200 if not MODEL_LOAD_ERROR else 500)


@app.route("/api/analyze-question", methods=["POST"])
def analyze_question():
    """
    Body: { "question": "Explain deadlock in operating systems" }

    Returns priority + (if a historical match is found) how many times it
    repeated, which papers, and its marks. Falls back to a pure ML
    prediction (priority only) if the question doesn't match known PYQs.
    """
    if MODEL_LOAD_ERROR:
        return jsonify({"error": f"Model failed to load: {MODEL_LOAD_ERROR}"}), 500

    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "Request body must be JSON with a 'question' field"}), 400

    question = data["question"]
    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "'question' must be a non-empty string"}), 400

    try:
        match = match_question_to_pyq(question)

        if match:
            response = {
                "question": question,
                "matched_topic": match["topic"],
                "subject": match["subject"],
                "section": match["section"],
                "priority": match["priority"],
                "times_repeated": f"{match['times_repeated']}/{match['total_papers']}",
                "repeat_percentage": round(
                    (match["times_repeated"] / match["total_papers"]) * 100, 1
                ) if match["total_papers"] else 0,
                "papers": match["papers"],
                "marks": match["marks"],
                "source": "pyq_history",
            }
        else:
            ml_result = ml_predict_priority(question)
            response = {
                "question": question,
                "matched_topic": None,
                "subject": None,
                "section": None,
                "priority": ml_result["priority"],
                "confidence": ml_result.get("confidence"),
                "class_confidences": ml_result.get("class_confidences"),
                "times_repeated": None,
                "repeat_percentage": None,
                "papers": [],
                "marks": [],
                "source": "ml_prediction",
                "note": "No exact match found in past papers — priority is a model estimate.",
            }

        return jsonify(response), 200

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Analysis failed", "detail": traceback.format_exc()}), 500


@app.route("/api/analyze-questions-batch", methods=["POST"])
def analyze_questions_batch():
    """Body: { "questions": ["Deadlock", "Paging", "RAID Levels"] }"""
    if MODEL_LOAD_ERROR:
        return jsonify({"error": f"Model failed to load: {MODEL_LOAD_ERROR}"}), 500

    data = request.get_json(silent=True)
    questions = data.get("questions") if data else None
    if not questions or not isinstance(questions, list):
        return jsonify({"error": "Request body must be JSON with a 'questions' list"}), 400

    results = []
    for q in questions:
        match = match_question_to_pyq(q)
        if match:
            results.append({
                "question": q,
                "matched_topic": match["topic"],
                "subject": match["subject"],
                "priority": match["priority"],
                "times_repeated": f"{match['times_repeated']}/{match['total_papers']}",
                "papers": match["papers"],
                "marks": match["marks"],
                "source": "pyq_history",
            })
        else:
            ml_result = ml_predict_priority(q)
            results.append({
                "question": q,
                "matched_topic": None,
                "priority": ml_result.get("priority"),
                "confidence": ml_result.get("confidence"),
                "times_repeated": None,
                "papers": [],
                "marks": [],
                "source": "ml_prediction",
            })

    return jsonify({"results": results}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
