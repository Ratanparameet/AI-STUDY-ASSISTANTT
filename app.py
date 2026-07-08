import os
import re
import csv
import pickle
import traceback
import random
import io
import numpy as np
import pdfplumber
import sqlite3
import jwt
import bcrypt
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

app = FastAPI(title="AI Study Assistant — Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PYQ_DATA_DIR = os.path.join(BASE_DIR, "dataset")

# JWT & Crypto Configuration
SECRET_KEY = "ai-study-assistant-jwt-secret-key-xyz-12345"
ALGORITHM = "HS256"

# Database path
DATABASE_FILE = os.path.join(BASE_DIR, "study_assistant.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            college TEXT DEFAULT '',
            branch TEXT DEFAULT '',
            semester TEXT DEFAULT '',
            profile_pic TEXT DEFAULT '',
            token_version INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'dark',
            notifications_enabled INTEGER DEFAULT 1,
            auto_save INTEGER DEFAULT 1,
            language TEXT DEFAULT 'English',
            theme_color TEXT DEFAULT '#a855f7',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # User Stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            todays_goal TEXT DEFAULT 'Complete 1 MCQ practice test',
            study_streak INTEGER DEFAULT 0,
            upcoming_test TEXT DEFAULT 'None scheduled',
            completed_chapters INTEGER DEFAULT 0,
            weak_chapters TEXT DEFAULT 'None',
            high_priority_left INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            remaining_tasks INTEGER DEFAULT 0,
            study_hours REAL DEFAULT 0.0,
            last_login TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # Notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    # History table (stores PDF uploads and MCQ tests)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'pdf_analysis' or 'mcq_test'
            filename TEXT,
            questions_count INTEGER DEFAULT 0,
            subject TEXT,
            report_json TEXT,
            score INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            percentage REAL DEFAULT 0.0,
            grade TEXT,
            time_taken TEXT,
            accuracy TEXT,
            weak_topics TEXT,
            strong_topics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as db_err:
    print(f"Database initialization error: {db_err}")

# Mount Static Files and templates
STATIC_DIR = os.path.join(BASE_DIR, "Frontend", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "Frontend", "templates"))

# Ensure css and js subdirectories exist
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

# Load ML model artifacts once at startup
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

PYQ_INDEX = []
PYQ_LOAD_ERRORS = []
db_vecs = None

def preprocess_text(text: str) -> str:
    # 1. Convert to lowercase
    text = text.lower()
    # 2. Remove punctuation and symbols (keep alphanumeric and spaces)
    import re
    text = re.sub(r'[^\w\s]', ' ', text)
    # 3. Normalize whitespace (remove double spaces, strip)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_pyq_data():
    global db_vecs
    csv_files = [
        ("Antennas and Propagation", os.path.join(PYQ_DATA_DIR, "processed", "updated_antennas_dataset.csv")),
        ("Embedded Systems", os.path.join(PYQ_DATA_DIR, "processed", "updated_embedded_dataset.csv"))
    ]
    
    for subject, path in csv_files:
        if not os.path.exists(path):
            PYQ_LOAD_ERRORS.append(f"File not found: {path}")
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    topic = (row.get("Question") or "").strip()
                    if not topic:
                        continue
                    
                    try:
                        times = int(row.get("Frequency", "0"))
                    except:
                        times = 0
                    
                    total = 9
                    
                    papers = [p.strip() for p in (row.get("Years_Appeared") or "").split(",") if p.strip()]
                    
                    try:
                        avg_marks = float(row.get("Average_Marks", "0") or "0")
                    except:
                        avg_marks = 0.0
                        
                    keywords = set(re.findall(r"\b\w{3,}\b", topic.lower()))
                    
                    PYQ_INDEX.append({
                        "subject": subject,
                        "section": (row.get("Chapter") or "").strip(),
                        "topic": topic,
                        "times_repeated": times,
                        "total_papers": total,
                        "papers": papers,
                        "marks": [f"{avg_marks:.1f} Marks"] if avg_marks > 0 else [],
                        "avg_marks": avg_marks,
                        "priority": (row.get("Priority") or "Low").strip(),
                        "keywords": keywords,
                        "difficulty": (row.get("Difficulty") or "Medium").strip(),
                    })
        except Exception as e:
            PYQ_LOAD_ERRORS.append(f"Failed to load {path}: {e}")

    # Build DB vectors matrix for fast cosine similarity comparisons
    if PYQ_INDEX and vectorizer is not None:
        all_topics_preprocessed = [preprocess_text(entry["topic"]) for entry in PYQ_INDEX]
        db_vecs = vectorizer.transform(all_topics_preprocessed)

load_pyq_data()

def ml_predict_priority(question_text: str):
    if MODEL_LOAD_ERROR or not model or not vectorizer:
        return {"priority": "Low", "source": "ml_prediction"}
        
    features = vectorizer.transform([question_text])
    priority = model.predict(features)[0]

    result = {"priority": str(priority), "source": "ml_prediction"}

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

def cosine_similarity_search(question_text: str):
    """
    Computes TF-IDF cosine similarity of question_text against the dataset database.
    """
    global db_vecs
    if db_vecs is None or vectorizer is None or not PYQ_INDEX:
        return None, 0.0
        
    # Preprocess using the identical logic
    q_clean = preprocess_text(question_text)
    
    q_vec = vectorizer.transform([q_clean])
    # Sparse matrix multiplication for fast cosine similarity since vectors are already TF-IDF normalized
    similarities = (q_vec * db_vecs.T).toarray()[0]
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])
    return PYQ_INDEX[best_idx], best_score

# In-memory session databases
ANALYSIS_HISTORY = []
TEST_HISTORY = []
ACTIVE_TESTS = {}  # Maps test_id -> {subject, questions} for grading exact test questions

# Dynamic MCQ Pools (20 Questions each)
MCQ_POOL = {
    "Embedded Systems": [
        {
            "id": "es_1",
            "question": "Which of the following is a key characteristic of an embedded system?",
            "options": [
                "A. General-purpose computation and high flexibility",
                "B. Real-time constraints and single-functioned execution",
                "C. Highly upgradable hardware components",
                "D. Large graphical user interface"
            ],
            "correct": "B",
            "explanation": "Embedded systems are generally single-functioned and must satisfy real-time constraints.",
            "chapter": "1. Introduction to Embedded Systems",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_2",
            "question": "What type of processor is designed for a specific application domain and allows custom instructions?",
            "options": [
                "A. General Purpose Processor (GPP)",
                "B. Application Specific Instruction-Set Processor (ASIP)",
                "C. Single Purpose Processor",
                "D. Complex Instruction Set Computer (CISC)"
            ],
            "correct": "B",
            "explanation": "ASIPs are optimized for specific domains and support tailored instruction sets.",
            "chapter": "1. Introduction to Embedded Systems",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_3",
            "question": "Which serial communication protocol uses a 2-wire interface consisting of SDA and SCL lines?",
            "options": [
                "A. Serial Peripheral Interface (SPI)",
                "B. Universal Asynchronous Receiver-Transmitter (UART)",
                "C. Inter-Integrated Circuit (I2C)",
                "D. Controller Area Network (CAN)"
            ],
            "correct": "C",
            "explanation": "I2C uses a Serial Data (SDA) line and a Serial Clock (SCL) line.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_4",
            "question": "Which protocol is widely used in automotive networks due to its high noise immunity and priority-based messaging?",
            "options": [
                "A. USB",
                "B. CAN Bus",
                "C. SPI",
                "D. RS-232"
            ],
            "correct": "B",
            "explanation": "The CAN bus is standard in automotive networks for robustness and priority-based arbitration.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_5",
            "question": "How many lines are typically required for basic SPI communication between a master and a single slave?",
            "options": [
                "A. 2 lines",
                "B. 3 lines",
                "C. 4 lines",
                "D. 8 lines"
            ],
            "correct": "C",
            "explanation": "SPI requires 4 lines: MOSI, MISO, SCLK, and SS (Slave Select).",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Easy",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_6",
            "question": "Which component is designed to reset the microcontroller if the software enters an infinite loop or freezes?",
            "options": [
                "A. Real Time Clock (RTC)",
                "B. Watchdog Timer (WDT)",
                "C. Brown Out Reset (BOR)",
                "D. Direct Memory Access (DMA)"
            ],
            "correct": "B",
            "explanation": "A Watchdog Timer resets the processor if the software fails to periodically kick/feed it.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_7",
            "question": "What does Brown Out Reset (BOR) protect an embedded system against?",
            "options": [
                "A. High operating temperature spikes",
                "B. Supply voltage drops below a safe threshold",
                "C. CPU frequency overdrive",
                "D. Memory overflow errors"
            ],
            "correct": "B",
            "explanation": "BOR holds the system in reset when the operating voltage falls below a critical level to prevent erratic behavior.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Hard",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_8",
            "question": "In an RTOS, what term describes a situation where a lower-priority task holds a resource needed by a higher-priority task?",
            "options": [
                "A. Deadlock",
                "B. Priority Inversion",
                "C. Starvation",
                "D. Race Condition"
            ],
            "correct": "B",
            "explanation": "Priority Inversion happens when a medium-priority task preempts a lower-priority task that is holding a mutex needed by a high-priority task.",
            "chapter": "3. RTOS",
            "difficulty": "Hard",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_9",
            "question": "Which scheduling algorithm assigns task priorities based on their periods, where tasks with shorter periods get higher priority?",
            "options": [
                "A. Round Robin Scheduling",
                "B. Rate Monotonic Scheduling (RMS)",
                "C. Earliest Deadline First (EDF)",
                "D. First In First Out (FIFO)"
            ],
            "correct": "B",
            "explanation": "RMS is a static-priority scheduling algorithm where priority is inversely proportional to task period.",
            "chapter": "3. RTOS",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_10",
            "question": "Which RTOS mechanism is best suited for task synchronization and mutual exclusion when accessing shared variables?",
            "options": [
                "A. Mutex or Semaphore",
                "B. Message Queue",
                "C. Mailbox",
                "D. Interrupt Service Routine (ISR)"
            ],
            "correct": "A",
            "explanation": "Mutexes and Semaphores are standard synchronization primitives for protecting shared resources.",
            "chapter": "3. RTOS",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_11",
            "question": "What is a system-on-chip (SoC)?",
            "options": [
                "A. A single board computer like Raspberry Pi",
                "B. An integrated circuit that integrates all components of a computer on a single chip",
                "C. A specialized memory chip",
                "D. A type of operating system"
            ],
            "correct": "B",
            "explanation": "A System-on-Chip (SoC) integrates components like CPU, memory, and peripheral ports onto a single integrated circuit.",
            "chapter": "1. Introduction to Embedded Systems",
            "difficulty": "Easy",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "es_12",
            "question": "Which of the following is an advantage of FPGA-based design compared to ASIC?",
            "options": [
                "A. Higher production cost at high volumes",
                "B. Reconfigurability and shorter time-to-market",
                "C. Maximum hardware speed possible",
                "D. Lowest possible power consumption"
            ],
            "correct": "B",
            "explanation": "FPGAs are reprogrammable, which allows fast prototyping, bug fixes, and faster development cycles than ASICs.",
            "chapter": "1. Introduction to Embedded Systems",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_13",
            "question": "Which bus architecture is commonly used in ARM-based microcontrollers for high-speed components?",
            "options": [
                "A. AHB (Advanced High-performance Bus)",
                "B. APB (Advanced Peripheral Bus)",
                "C. I2C Bus",
                "D. CAN Bus"
            ],
            "correct": "A",
            "explanation": "AHB is part of the AMBA specification used for high-performance, high-clock-frequency system modules.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_14",
            "question": "What is the primary role of a linker script in an embedded systems toolchain?",
            "options": [
                "A. To translate C code into assembly",
                "B. To define memory map layouts (Flash, RAM) and section placement",
                "C. To compress the compiled binary file",
                "D. To load the program into the microcontroller"
            ],
            "correct": "B",
            "explanation": "Linker scripts instruct the linker on memory organization, mapping compiled code and data sections to specific addresses.",
            "chapter": "4. Compiling and Linking",
            "difficulty": "Hard",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "es_15",
            "question": "Which of the following is a characteristic of a hard real-time system?",
            "options": [
                "A. Deadlines can be missed occasionally with reduced quality of service",
                "B. Missing a deadline results in total system failure",
                "C. Prioritizes average throughput over latency",
                "D. Does not require deterministic behavior"
            ],
            "correct": "B",
            "explanation": "In a hard real-time system, missing even a single deadline is considered a catastrophic failure.",
            "chapter": "3. RTOS",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_16",
            "question": "What is the purpose of the program counter (PC) register in a microcontroller?",
            "options": [
                "A. To store the address of the next instruction to be executed",
                "B. To count the number of successfully executed loops",
                "C. To act as a temporary general-purpose register",
                "D. To hold the status flags of the ALU"
            ],
            "correct": "A",
            "explanation": "The program counter points to the address of the instruction currently being fetched or executed.",
            "chapter": "1. Introduction to Embedded Systems",
            "difficulty": "Easy",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "es_17",
            "question": "Which interface is specifically optimized for debugging and testing microcontrollers in-circuit?",
            "options": [
                "A. JTAG / SWD",
                "B. RS-232",
                "C. SPI",
                "D. Ethernet"
            ],
            "correct": "A",
            "explanation": "JTAG and Serial Wire Debug (SWD) are hardware interfaces for debugging and programming MCUs.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "es_18",
            "question": "Which of the following is true about standard interrupt service routines (ISRs)?",
            "options": [
                "A. ISRs can take arguments and return values",
                "B. ISRs should be as short and fast as possible",
                "C. ISRs can perform heavy block I/O operations",
                "D. ISRs run inside task context"
            ],
            "correct": "B",
            "explanation": "ISRs should execute quickly to minimize latency and avoid blocking other low-latency events.",
            "chapter": "3. RTOS",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_19",
            "question": "In an embedded system, what is the main purpose of DMA (Direct Memory Access)?",
            "options": [
                "A. To handle arithmetic and logic computations",
                "B. To transfer data between memory and peripherals without CPU intervention",
                "C. To encrypt stored passwords in flash memory",
                "D. To boot the operating system kernel"
            ],
            "correct": "B",
            "explanation": "DMA offloads data transfers from the CPU, allowing the CPU to perform other computational tasks or enter sleep states.",
            "chapter": "2. Device and Communication Buses",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "es_20",
            "question": "What does 'concurrency' mean in the context of an RTOS?",
            "options": [
                "A. Executing multiple tasks simultaneously on a single CPU core",
                "B. Managing multiple active tasks by switching execution rapidly (interleaving)",
                "C. Designing circuits with multiple processors",
                "D. Synchronous execution of all instructions"
            ],
            "correct": "B",
            "explanation": "On a single-core CPU, RTOS tasks run concurrently by rapid interleaving (context switching), creating the illusion of parallel execution.",
            "chapter": "3. RTOS",
            "difficulty": "Medium",
            "priority": "Low",
            "marks": 1
        }
    ],
    "Antennas and Propagation": [
        {
            "id": "ap_1",
            "question": "Which antenna parameter represents the ratio of radiation intensity in a given direction to average radiation intensity?",
            "options": [
                "A. Directivity",
                "B. Antenna Efficiency",
                "C. Gain",
                "D. Radiation Resistance"
            ],
            "correct": "A",
            "explanation": "Directivity is the ratio of maximum radiation intensity to average radiation intensity.",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_2",
            "question": "What is the radiation resistance of an ideal half-wave dipole in free space?",
            "options": [
                "A. 50 Ohms",
                "B. 73 Ohms",
                "C. 120 Ohms",
                "D. 377 Ohms"
            ],
            "correct": "B",
            "explanation": "A half-wave dipole antenna has an input impedance whose real part is approximately 73 Ohms in free space.",
            "chapter": "2. Radiation of Electric dipole",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_3",
            "question": "Which equation correctly relates antenna Gain, Directivity, and Efficiency?",
            "options": [
                "A. Gain = Efficiency / Directivity",
                "B. Gain = Efficiency * Directivity",
                "C. Gain = Directivity / Efficiency",
                "D. Gain = Efficiency + Directivity"
            ],
            "correct": "B",
            "explanation": "Antenna gain is efficiency times directivity: G = eta * D.",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Easy",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_4",
            "question": "What constitutes a short dipole antenna?",
            "options": [
                "A. An antenna whose length is much smaller than the wavelength (L << lambda/10)",
                "B. An antenna operating at ultra-high frequencies",
                "C. An antenna with high directivity",
                "D. An antenna with no reactive impedance"
            ],
            "correct": "A",
            "explanation": "A short dipole is defined by physical length significantly shorter than a tenth of a wavelength.",
            "chapter": "2. Radiation of Electric dipole",
            "difficulty": "Medium",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "ap_5",
            "question": "How does the radiation resistance of a small circular loop antenna scale with the loop area?",
            "options": [
                "A. Proportional to Area",
                "B. Proportional to Area squared",
                "C. Inversely proportional to Area",
                "D. Independent of Area"
            ],
            "correct": "B",
            "explanation": "The radiation resistance of a small loop antenna is proportional to the square of its area (R_r proportional to (A/lambda^2)^2).",
            "chapter": "2. Radiation of Electric dipole",
            "difficulty": "Hard",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_6",
            "question": "In a broadside antenna array, what is the required excitation phase difference between adjacent elements?",
            "options": [
                "A. 0 degrees",
                "B. 90 degrees",
                "C. 180 degrees",
                "D. 360 degrees / number of elements"
            ],
            "correct": "A",
            "explanation": "In a broadside array, all elements are fed in phase (phase difference is 0) to maximize radiation perpendicular to the array axis.",
            "chapter": "Array Antenna",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_7",
            "question": "Which array type has its maximum radiation direction along the axis of the array?",
            "options": [
                "A. Broadside Array",
                "B. End-Fire Array",
                "C. Collinear Array",
                "D. Phased Array"
            ],
            "correct": "B",
            "explanation": "An end-fire array directs its main beam along the line of the array.",
            "chapter": "Array Antenna",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_8",
            "question": "Which propagation mode is primarily used for long-distance High-Frequency (HF) communication via reflection from the ionosphere?",
            "options": [
                "A. Ground Wave Propagation",
                "B. Space Wave Propagation",
                "C. Sky Wave Propagation",
                "D. Tropospheric Scatter"
            ],
            "correct": "C",
            "explanation": "Sky waves are reflected by the ionospheric layers, enabling long-distance shortwave communications.",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_9",
            "question": "Which ionospheric layer is mainly responsible for reflecting high-frequency waves back to Earth during day-time?",
            "options": [
                "A. D Layer",
                "B. E Layer",
                "C. F2 Layer",
                "D. C Layer"
            ],
            "correct": "C",
            "explanation": "The F2 layer is the highest and most ionized layer of the ionosphere, reflecting the highest frequency waves back to Earth.",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_10",
            "question": "What is the definition of Skip Distance in radio wave propagation?",
            "options": [
                "A. The distance between the transmitter and the radio horizon",
                "B. The minimum distance from a transmitter at which a sky wave of a given frequency returns to Earth",
                "C. The height of the equivalent reflecting layer",
                "D. The maximum range of space wave propagation"
            ],
            "correct": "B",
            "explanation": "Skip distance is the shortest distance from the transmitter where a sky wave of a specific frequency can be received.",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_11",
            "question": "How is the critical frequency (f_c) of an ionospheric layer calculated from its maximum electron density (N_max in m^-3)?",
            "options": [
                "A. f_c ≈ 9 * sqrt(N_max)",
                "B. f_c ≈ 81 * N_max",
                "C. f_c ≈ 9 * N_max",
                "D. f_c ≈ sqrt(9 * N_max)"
            ],
            "correct": "A",
            "explanation": "Critical frequency f_c is approximately equal to 9 * sqrt(N_max).",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Hard",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_12",
            "question": "What does the term Duct Propagation refer to in radio wave propagation?",
            "options": [
                "A. Propagation of waves along metal tubes",
                "B. Bending of waves due to temperature inversion in the troposphere, trapping them in a boundary layer",
                "C. Reflection of waves by the ground surface",
                "D. Attenuation of waves by rain and foliage"
            ],
            "correct": "B",
            "explanation": "Duct propagation occurs under special atmospheric conditions (like temperature inversions) that trap radio waves, causing them to travel long distances inside a duct.",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Hard",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "ap_13",
            "question": "What is the intrinsic impedance of free space?",
            "options": [
                "A. 50 Ohms",
                "B. 120 Ohms",
                "C. 377 Ohms",
                "D. 73 Ohms"
            ],
            "correct": "C",
            "explanation": "The intrinsic impedance of free space is exactly 120 * pi, or approximately 377 Ohms.",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Easy",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "ap_14",
            "question": "Which of the following describes the polarization of an antenna?",
            "options": [
                "A. The physical orientation of the antenna structure",
                "B. The orientation of the electric field vector of the radiated wave over time",
                "C. The direction of maximum radiation intensity",
                "D. The input impedance phase angle"
            ],
            "correct": "B",
            "explanation": "Antenna polarization refers to the orientation of the electric field vector (E-field) of the wave it transmits.",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_15",
            "question": "Which formula relates the effective aperture (A_e) and gain (G) of an antenna?",
            "options": [
                "A. A_e = G * lambda^2 / (4 * pi)",
                "B. A_e = G * 4 * pi / lambda^2",
                "C. A_e = G * lambda / (2 * pi)",
                "D. A_e = G * pi * lambda"
            ],
            "correct": "A",
            "explanation": "The effective aperture is related to the gain by A_e = (lambda^2 * G) / (4 * pi).",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Hard",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_16",
            "question": "What is the primary advantage of a folded dipole antenna over a simple half-wave dipole?",
            "options": [
                "A. It has a significantly higher gain",
                "B. Its input impedance is four times higher (approx. 300 Ohms), providing a better match for twin-lead cables",
                "C. It has an omnidirectional radiation pattern",
                "D. It is physically much smaller"
            ],
            "correct": "B",
            "explanation": "A folded dipole has an input impedance of about 300 Ohms, making it ideal for matching 300-Ohm feedlines.",
            "chapter": "2. Radiation of Electric dipole",
            "difficulty": "Medium",
            "priority": "Medium",
            "marks": 1
        },
        {
            "id": "ap_17",
            "question": "In an antenna array, what does the 'Array Factor' depend on?",
            "options": [
                "A. The material of the antenna elements",
                "B. The spacing, number, relative amplitude, and phase excitation of the array elements",
                "C. The radiation characteristics of a single element",
                "D. The transmitter power level"
            ],
            "correct": "B",
            "explanation": "The Array Factor represents the radiation pattern of the array assuming isotropic elements, determined by geometry and excitation.",
            "chapter": "Array Antenna",
            "difficulty": "Hard",
            "priority": "Low",
            "marks": 1
        },
        {
            "id": "ap_18",
            "question": "What is the beamwidth between first nulls (BWFN) of an antenna pattern?",
            "options": [
                "A. The angular width between the points where the power density drops to half maximum (-3dB)",
                "B. The angular width between the directions containing the first zero-radiation points (nulls) around the main lobe",
                "C. The total angle of the back lobe",
                "D. The phase margin at first resonance"
            ],
            "correct": "B",
            "explanation": "BWFN is the angle between the two first nulls adjacent to the main beam.",
            "chapter": "1. Basic antenna concepts",
            "difficulty": "Medium",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_19",
            "question": "Which antenna type consists of a feed element, a reflector, and one or more directors to achieve high directivity?",
            "options": [
                "A. Half-wave Dipole",
                "B. Yagi-Uda Antenna",
                "C. Parabolic Reflector",
                "D. Microstrip Patch Antenna"
            ],
            "correct": "B",
            "explanation": "A Yagi-Uda antenna is a directional antenna consisting of an active dipole and passive elements (reflector and directors).",
            "chapter": "Yagi-Uda",
            "difficulty": "Easy",
            "priority": "High",
            "marks": 1
        },
        {
            "id": "ap_20",
            "question": "What represents the 'Skip Zone' in sky wave propagation?",
            "options": [
                "A. The area beyond the line-of-sight range of space waves",
                "B. The region between the limit of ground wave coverage and the point where the first sky wave returns to Earth",
                "C. The area directly under the ionospheric reflection point",
                "D. The maximum altitude of wave propagation"
            ],
            "correct": "B",
            "explanation": "The skip zone is the silent zone where neither ground waves nor sky waves can be received.",
            "chapter": "15. Radio wave propagation",
            "difficulty": "Medium",
            "priority": "Low",
            "marks": 1
        }
    ]
}

# Pydantic Request Models
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    college: Optional[str] = ""
    branch: Optional[str] = ""
    semester: Optional[str] = ""

class LoginRequest(BaseModel):
    email_or_username: str
    password: str
    remember_me: Optional[bool] = False

class UpdateProfileRequest(BaseModel):
    name: str
    email: str
    college: Optional[str] = ""
    branch: Optional[str] = ""
    semester: Optional[str] = ""
    profile_photo: Optional[str] = ""

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

class UpdateSettingsRequest(BaseModel):
    theme: str
    notifications_enabled: bool
    auto_save: bool
    language: str
    theme_color: str

# Temporary store for forgot password reset codes
RESET_CODES = {} # maps email -> (code, expiry)

# JWT Helper functions
def generate_jwt(username: str, token_version: int, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": username,
        "version": token_version,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(request: Request) -> int:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_version = payload.get("version")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        conn = get_db_connection()
        user = conn.execute("SELECT id, token_version FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user["token_version"] != token_version:
            raise HTTPException(status_code=401, detail="Session expired")
            
        return user["id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Authentication & User Management Routes

@app.post("/register")
async def register(req: RegisterRequest):
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", req.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", req.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", req.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"\d", req.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", req.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")

    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, college, branch, semester) VALUES (?, ?, ?, ?, ?, ?)",
            (req.username, req.email, password_hash, req.college, req.branch, req.semester)
        )
        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
        cursor.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (user_id, "Welcome to StudyAI! Complete your profile to get started.", "Welcome")
        )
        
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/login")
async def login(req: LoginRequest):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR username = ?",
        (req.email_or_username, req.email_or_username)
    ).fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid username/email or password")
        
    if not bcrypt.checkpw(req.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid username/email or password")
        
    expires = timedelta(days=30) if req.remember_me else timedelta(hours=24)
    token = generate_jwt(user["username"], user["token_version"], expires)
    
    conn.execute(
        "UPDATE user_stats SET last_login = ? WHERE user_id = ?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"])
    )
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "token": token,
        "username": user["username"],
        "email": user["email"],
        "message": "Logged in successfully"
    }

@app.post("/logout")
async def logout(request: Request):
    return {"success": True, "message": "Logged out successfully"}

@app.post("/logout-all")
async def logout_all(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    conn.execute("UPDATE users SET token_version = token_version + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Logged out of all devices successfully"}

@app.get("/profile")
async def get_profile(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    user = conn.execute("SELECT username, email, college, branch, semester, profile_pic FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "name": user["username"],
        "email": user["email"],
        "college": user["college"],
        "branch": user["branch"],
        "semester": user["semester"],
        "profile_photo": user["profile_pic"]
    }

@app.post("/update-profile")
async def update_profile(request: Request, req: UpdateProfileRequest):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE users SET username = ?, email = ?, college = ?, branch = ?, semester = ?, profile_pic = ? WHERE id = ?",
            (req.name, req.email, req.college, req.branch, req.semester, req.profile_photo, user_id)
        )
        conn.commit()
        
        conn.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (user_id, "Profile updated successfully.", "Profile Update")
        )
        conn.commit()
        
        return {"success": True, "message": "Profile updated successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already in use")
    finally:
        conn.close()

@app.post("/change-password")
async def change_password(request: Request, req: ChangePasswordRequest):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    user = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or not bcrypt.checkpw(req.old_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        conn.close()
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    if len(req.new_password) < 8 or not re.search(r"[A-Z]", req.new_password) or not re.search(r"[a-z]", req.new_password) or not re.search(r"\d", req.new_password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", req.new_password):
         conn.close()
         raise HTTPException(status_code=400, detail="New password does not meet strength requirements")
         
    new_hash = bcrypt.hashpw(req.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Password changed successfully"}

@app.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
        
    import random
    code = str(random.randint(100000, 999999))
    RESET_CODES[req.email] = (code, datetime.now() + timedelta(minutes=15))
    
    return {
        "success": True, 
        "message": "Password reset code generated",
        "code": code
    }

@app.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if req.email not in RESET_CODES:
        raise HTTPException(status_code=400, detail="No reset code requested for this email")
        
    saved_code, expiry = RESET_CODES[req.email]
    if datetime.now() > expiry:
        del RESET_CODES[req.email]
        raise HTTPException(status_code=400, detail="Reset code has expired")
        
    if req.code != saved_code:
        raise HTTPException(status_code=400, detail="Invalid reset code")
        
    if len(req.new_password) < 8 or not re.search(r"[A-Z]", req.new_password) or not re.search(r"[a-z]", req.new_password) or not re.search(r"\d", req.new_password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", req.new_password):
         raise HTTPException(status_code=400, detail="New password does not meet strength requirements")
         
    new_hash = bcrypt.hashpw(req.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_db_connection()
    conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, req.email))
    conn.commit()
    conn.close()
    
    del RESET_CODES[req.email]
    return {"success": True, "message": "Password reset successfully"}

@app.get("/settings")
async def get_settings(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    sett = conn.execute("SELECT theme, notifications_enabled, auto_save, language, theme_color FROM settings WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not sett:
        return {
            "theme": "dark",
            "notifications_enabled": True,
            "auto_save": True,
            "language": "English",
            "theme_color": "#a855f7"
        }
    return {
        "theme": sett["theme"],
        "notifications_enabled": bool(sett["notifications_enabled"]),
        "auto_save": bool(sett["auto_save"]),
        "language": sett["language"],
        "theme_color": sett["theme_color"]
    }

@app.post("/settings")
async def update_settings(request: Request, req: UpdateSettingsRequest):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    conn.execute(
        "UPDATE settings SET theme = ?, notifications_enabled = ?, auto_save = ?, language = ?, theme_color = ? WHERE user_id = ?",
        (req.theme, int(req.notifications_enabled), int(req.auto_save), req.language, req.theme_color, user_id)
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": "Settings updated successfully"}

@app.get("/notifications")
async def get_notifications(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    notifs = conn.execute("SELECT id, message, type, is_read, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,)).fetchall()
    conn.close()
    return [dict(n) for n in notifs]

@app.post("/notifications/read")
async def mark_notifications_read(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/notifications/clear")
async def clear_notifications(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# HTTP Routes — Page Serving
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/welcome", response_class=HTMLResponse)
def welcome_page(request: Request):
    return templates.TemplateResponse(request, "welcome.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request, "register.html")

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "forgot_password.html")

@app.get("/api/health")
def health():
    return {
        "status": "ok" if not MODEL_LOAD_ERROR else "error",
        "model_error": MODEL_LOAD_ERROR,
        "model_classes": list(model.classes_) if model is not None else None,
        "pyq_topics_loaded": len(PYQ_INDEX),
        "pyq_load_errors": PYQ_LOAD_ERRORS,
    }

@app.post("/api/analyze-question")
async def api_analyze_question(request: Request):
    user_id = get_current_user_id(request)
    if MODEL_LOAD_ERROR:
         raise HTTPException(status_code=500, detail=f"Model failed to load: {MODEL_LOAD_ERROR}")
    
    data = await request.json()
    question = data.get("question")
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="'question' must be a non-empty string")
        
    match = match_question_to_pyq(question)
    if match:
        response = {
            "question": question,
            "matched_topic": match["topic"],
            "subject": match["subject"],
            "section": match["section"],
            "priority": match["priority"],
            "times_repeated": f"{match['times_repeated']}/{match['total_papers']}",
            "repeat_percentage": round((match["times_repeated"] / match["total_papers"]) * 100, 1) if match["total_papers"] else 0,
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
    return response

@app.post("/api/analyze-questions-batch")
async def api_analyze_questions_batch(request: Request):
    user_id = get_current_user_id(request)
    if MODEL_LOAD_ERROR:
         raise HTTPException(status_code=500, detail=f"Model failed to load: {MODEL_LOAD_ERROR}")
         
    data = await request.json()
    questions = data.get("questions")
    filename = data.get("filename", "batch_analysis")
    if not questions or not isinstance(questions, list):
         raise HTTPException(status_code=400, detail="Request body must be JSON with a 'questions' list")

    # Initialize tracking variables
    subject_counts = {}
    chapter_counts = {}
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    analyzed_list = []
         
    for q in questions:
        match, similarity = cosine_similarity_search(q)
        if match and similarity >= 0.30:
            subj = match["subject"]
            subject_counts[subj] = subject_counts.get(subj, 0) + 1
            chap = match["section"]
            chapter_counts[chap] = chapter_counts.get(chap, 0) + 1
            priority = match["priority"]
            priority_counts[priority] += 1
            freq = match["times_repeated"]
            avg_marks = match["avg_marks"]
            difficulty = match["difficulty"]
            
            sim_w = similarity * 40
            freq_w = min(freq / 8.0, 1.0) * 20
            pri_w = {"High": 20, "Medium": 12, "Low": 5}.get(priority, 5)
            marks_w = min(avg_marks / 10.0, 1.0) * 20
            importance = int(min(max(sim_w + freq_w + pri_w + marks_w, 10), 99))
            
            analyzed_list.append({
                "status": "found",
                "question": q,
                "matched_topic": match["topic"],
                "priority": priority,
                "importance": importance,
                "repeated": freq,
                "difficulty": difficulty,
                "avg_marks": avg_marks,
                "recommendation": "Study First" if priority == "High" else "Review Later",
                "subject": subj,
                "chapter": chap,
                "similarity": round(similarity, 2)
            })
        else:
            # Use ML model prediction as fallback
            ml_result = ml_predict_priority(q)
            analyzed_list.append({
                "status": "not_found",
                "question": q,
                "matched_topic": match["topic"] if match else "N/A",
                "priority": ml_result["priority"],
                "importance": 25,
                "repeated": 0,
                "difficulty": "Medium",
                "avg_marks": 0,
                "recommendation": "Review Later",
                "subject": "General",
                "chapter": "Uncategorized",
                "similarity": round(similarity, 2) if match else 0.0,
                "message": "This question is not available in the current dataset."
            })

    dominant_subject = "Embedded Systems"
    if subject_counts:
        dominant_subject = max(subject_counts, key=subject_counts.get)
    
    most_repeated_chapter = "Uncategorized"
    if chapter_counts:
        most_repeated_chapter = max(chapter_counts, key=chapter_counts.get)
        
    weak_chapters = [chap for chap, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True)[:2]]
    if not weak_chapters:
        weak_chapters = ["General"]
        
    recommended_time = f"{priority_counts['High'] * 2 + priority_counts['Medium'] * 1 + 2} Hours"
    found_count = len([x for x in analyzed_list if x.get("status") == "found"])
    coverage = min(95, int(50 + found_count * 1.5))
    
    report = {
        "total_questions": len(questions),
        "matched_questions": found_count,
        "not_found_questions": len(questions) - found_count,
        "generate_dashboard": found_count > 0,
        "high_priority": priority_counts["High"] if found_count > 0 else 0,
        "medium_priority": priority_counts["Medium"] if found_count > 0 else 0,
        "low_priority": priority_counts["Low"] if found_count > 0 else 0,
        "most_repeated_chapter": most_repeated_chapter if found_count > 0 else "N/A",
        "weak_chapters": ", ".join(weak_chapters) if found_count > 0 else "N/A",
        "recommended_study_time": recommended_time if found_count > 0 else "Not Available",
        "estimated_coverage": f"{coverage}%" if found_count > 0 else "0%",
        "subject": dominant_subject if found_count > 0 else "General"
    }
    
    result_data = {
        "filename": filename,
        "questions": analyzed_list,
        "report": report
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (user_id, type, filename, questions_count, subject, report_json) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, "pdf_analysis", filename, len(questions), report["subject"], json.dumps(report))
    )
    cursor.execute(
        "UPDATE user_stats SET high_priority_left = high_priority_left + ?, weak_chapters = ?, completed_chapters = completed_chapters + 1 WHERE user_id = ?",
        (report["high_priority"], report["weak_chapters"], user_id)
    )
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"PDF '{filename}' uploaded and analyzed successfully. {len(questions)} questions extracted.", "Analysis Completed")
    )
    conn.commit()
    conn.close()
    
    return result_data

@app.post("/upload-pdf")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Upload a PDF question paper, extract questions, and run batch analysis."""
    user_id = get_current_user_id(request)
    if MODEL_LOAD_ERROR:
        raise HTTPException(status_code=500, detail=f"Model failed to load: {MODEL_LOAD_ERROR}")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    # Extract questions from PDF
    questions = extract_questions_from_pdf(file_bytes)
    filename = file.filename
    
    # Run the same analysis logic
    subject_counts = {}
    chapter_counts = {}
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    analyzed_list = []
    
    for q in questions:
        match, similarity = cosine_similarity_search(q)
        if match and similarity >= 0.30:
            subj = match["subject"]
            subject_counts[subj] = subject_counts.get(subj, 0) + 1
            chap = match["section"]
            chapter_counts[chap] = chapter_counts.get(chap, 0) + 1
            priority = match["priority"]
            priority_counts[priority] += 1
            freq = match["times_repeated"]
            avg_marks = match["avg_marks"]
            difficulty = match["difficulty"]
            
            sim_w = similarity * 40
            freq_w = min(freq / 8.0, 1.0) * 20
            pri_w = {"High": 20, "Medium": 12, "Low": 5}.get(priority, 5)
            marks_w = min(avg_marks / 10.0, 1.0) * 20
            importance = int(min(max(sim_w + freq_w + pri_w + marks_w, 10), 99))
            
            analyzed_list.append({
                "status": "found",
                "question": q,
                "matched_topic": match["topic"],
                "priority": priority,
                "importance": importance,
                "repeated": freq,
                "difficulty": difficulty,
                "avg_marks": avg_marks,
                "recommendation": "Study First" if priority == "High" else "Review Later",
                "subject": subj,
                "chapter": chap,
                "similarity": round(similarity, 2)
            })
        else:
            ml_result = ml_predict_priority(q)
            analyzed_list.append({
                "status": "not_found",
                "question": q,
                "matched_topic": match["topic"] if match else "N/A",
                "priority": ml_result["priority"],
                "importance": 25,
                "repeated": 0,
                "difficulty": "Medium",
                "avg_marks": 0,
                "recommendation": "Review Later",
                "subject": "General",
                "chapter": "Uncategorized",
                "similarity": round(similarity, 2) if match else 0.0,
                "message": "Not found in dataset — priority estimated by ML model."
            })
    
    dominant_subject = "Embedded Systems"
    if subject_counts:
        dominant_subject = max(subject_counts, key=subject_counts.get)
    
    most_repeated_chapter = "Uncategorized"
    if chapter_counts:
        most_repeated_chapter = max(chapter_counts, key=chapter_counts.get)
    
    weak_chapters = [chap for chap, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True)[:2]]
    if not weak_chapters:
        weak_chapters = ["General"]
    
    recommended_time = f"{priority_counts['High'] * 2 + priority_counts['Medium'] * 1 + 2} Hours"
    found_count = len([x for x in analyzed_list if x.get("status") == "found"])
    coverage = min(95, int(50 + found_count * 1.5))
    
    report = {
        "total_questions": len(questions),
        "matched_questions": found_count,
        "not_found_questions": len(questions) - found_count,
        "generate_dashboard": found_count > 0,
        "high_priority": priority_counts["High"],
        "medium_priority": priority_counts["Medium"],
        "low_priority": priority_counts["Low"],
        "most_repeated_chapter": most_repeated_chapter,
        "weak_chapters": ", ".join(weak_chapters),
        "recommended_study_time": recommended_time,
        "estimated_coverage": f"{coverage}%",
        "subject": dominant_subject
    }
    
    result_data = {
        "filename": filename,
        "questions": analyzed_list,
        "report": report
    }
    
    # Save to history
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (user_id, type, filename, questions_count, subject, report_json) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, "pdf_analysis", filename, len(questions), report["subject"], json.dumps(report))
    )
    cursor.execute(
        "UPDATE user_stats SET high_priority_left = high_priority_left + ?, weak_chapters = ?, completed_chapters = completed_chapters + 1 WHERE user_id = ?",
        (report["high_priority"], report["weak_chapters"], user_id)
    )
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"PDF '{filename}' uploaded and analyzed. {len(questions)} questions extracted.", "Analysis Completed")
    )
    conn.commit()
    conn.close()
    
    return result_data

@app.post("/generate-mcq")
async def generate_mcq(request: Request):
    user_id = get_current_user_id(request)
    data = await request.json()
    subject = data.get("subject", "Embedded Systems")
    exam_type = data.get("exam_type", "Full Syllabus Mock Test")
    
    pool = MCQ_POOL.get(subject, MCQ_POOL["Embedded Systems"])
    
    # 5 different exam types for both Embedded Systems and AWP
    if exam_type == "Unit Test I: Core Concepts":
        selected_questions = pool[:10]
    elif exam_type == "Unit Test II: Advanced Applications":
        selected_questions = pool[10:20]
    elif exam_type == "High-Priority PYQ Focus":
        priority_qs = [q for q in pool if q.get("priority") in ("High", "Medium")]
        selected_questions = random.sample(priority_qs, min(10, len(priority_qs)))
    elif exam_type == "Quick Practice Quiz":
        selected_questions = random.sample(pool, min(10, len(pool)))
    else: # Full Syllabus Mock Test
        selected_questions = random.sample(pool, min(20, len(pool)))
    
    test_id = random.randint(100000, 999999)
    ACTIVE_TESTS[test_id] = {
        "subject": subject,
        "questions": selected_questions,
        "user_id": user_id
    }
    
    client_questions = []
    for q in selected_questions:
        client_questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "difficulty": q["difficulty"],
            "priority": q["priority"]
        })
    
    return {"test_id": test_id, "questions": client_questions, "subject": subject}

@app.post("/submit-test")
async def submit_test(request: Request):
    user_id = get_current_user_id(request)
    data = await request.json()
    test_id = data.get("test_id")
    subject = data.get("subject", "Embedded Systems")
    answers_raw = data.get("answers", {})
    time_taken = data.get("time_taken", 120)

    answers = {}
    if isinstance(answers_raw, list):
        for item in answers_raw:
            qid = str(item.get("question_id", item.get("id", "")))
            sel = item.get("selected_option", item.get("answer", "")).strip().upper()
            if qid:
                answers[qid] = sel
    elif isinstance(answers_raw, dict):
        for k, v in answers_raw.items():
            answers[str(k)] = str(v).strip().upper() if v else ""

    test_id_int = int(test_id) if test_id else None
    if test_id_int and test_id_int in ACTIVE_TESTS and ACTIVE_TESTS[test_id_int]["user_id"] == user_id:
        selected_questions = ACTIVE_TESTS[test_id_int]["questions"]
    else:
        pool = MCQ_POOL.get(subject, MCQ_POOL["Embedded Systems"])
        if answers:
            selected_questions = [q for q in pool if str(q["id"]) in answers]
        else:
            selected_questions = pool[:20]

    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    graded_details = []
    weak_topics_counts = {}
    strong_topics_counts = {}

    for q in selected_questions:
        q_id_str = str(q["id"])
        user_ans = answers.get(q_id_str, "").strip().upper()
        correct_ans = q["correct"].strip().upper()
        is_correct = False
        is_skipped = False

        if not user_ans:
            is_skipped = True
            skipped_count += 1
        elif user_ans == correct_ans:
            is_correct = True
            correct_count += 1
            strong_topics_counts[q["chapter"]] = strong_topics_counts.get(q["chapter"], 0) + 1
        else:
            wrong_count += 1
            weak_topics_counts[q["chapter"]] = weak_topics_counts.get(q["chapter"], 0) + 1

        user_option_text = "Skipped"
        correct_option_text = ""
        for opt in q["options"]:
            opt_letter = opt.strip()[0].upper() if opt.strip() else ""
            if opt_letter == correct_ans:
                correct_option_text = opt
            if user_ans and opt_letter == user_ans:
                user_option_text = opt

        graded_details.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "student_answer": user_option_text,
            "correct_answer": correct_option_text,
            "is_correct": is_correct,
            "is_skipped": is_skipped,
            "explanation": q["explanation"],
            "chapter": q["chapter"],
            "difficulty": q["difficulty"],
            "priority": q["priority"],
            "marks": q["marks"]
        })

    total_q = len(selected_questions) or 20
    percentage = round((correct_count / total_q) * 100, 1)
    accuracy = round((correct_count / (correct_count + wrong_count)) * 100, 1) if (correct_count + wrong_count) > 0 else 0

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    weak_topics = [topic for topic, count in sorted(weak_topics_counts.items(), key=lambda x: x[1], reverse=True)]
    strong_topics = [topic for topic, count in sorted(strong_topics_counts.items(), key=lambda x: x[1], reverse=True)]

    if not weak_topics:
        weak_topics = ["None — Excellent across all topics!"]
    if not strong_topics:
        strong_topics = ["None"]

    result_summary = {
        "subject": subject,
        "score": correct_count,
        "total": total_q,
        "percentage": percentage,
        "correct": correct_count,
        "wrong": wrong_count,
        "skipped": skipped_count,
        "grade": grade,
        "time_taken": f"{time_taken // 60}m {time_taken % 60}s",
        "accuracy": f"{accuracy}%",
        "weak_topics": ", ".join(weak_topics[:2]),
        "strong_topics": ", ".join(strong_topics[:2]),
        "graded_details": graded_details
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO history 
           (user_id, type, subject, questions_count, score, total, percentage, grade, time_taken, accuracy, weak_topics, strong_topics, report_json) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, "mcq_test", subject, total_q, correct_count, total_q, percentage, grade, 
         result_summary["time_taken"], result_summary["accuracy"], result_summary["weak_topics"], 
         result_summary["strong_topics"], json.dumps(graded_details))
    )
    inserted_test_id = cursor.lastrowid
    result_summary["test_id"] = inserted_test_id
    
    stats = conn.execute("SELECT study_streak, high_priority_left, study_hours, completed_tasks FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    current_streak = stats["study_streak"] if stats else 0
    new_streak = current_streak + 1
    
    high_priority_solved = sum(1 for q in graded_details if q["priority"] == "High" and q["is_correct"])
    new_hp_left = max(0, (stats["high_priority_left"] if stats else 0) - high_priority_solved)
    new_study_hours = (stats["study_hours"] if stats else 0) + round(time_taken / 3600.0 + 0.2, 1)
    new_completed_tasks = (stats["completed_tasks"] if stats else 0) + 1
    
    cursor.execute(
        """UPDATE user_stats SET 
           study_streak = ?, 
           high_priority_left = ?, 
           study_hours = ?, 
           completed_tasks = ?, 
           remaining_tasks = ?, 
           weak_chapters = ? 
           WHERE user_id = ?""",
        (new_streak, new_hp_left, new_study_hours, new_completed_tasks, max(0, 5 - new_completed_tasks), result_summary["weak_topics"], user_id)
    )
    
    cursor.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"MCQ Practice Test Completed! Score: {correct_count}/{total_q} ({percentage}%). Grade: {grade}.", "MCQ Test Completed")
    )
    
    if new_completed_tasks >= 1:
        cursor.execute(
            "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
            (user_id, "Congratulations! Today's Study Goal Completed.", "Study Goal Completed")
        )
        
    conn.commit()
    conn.close()

    if test_id_int in ACTIVE_TESTS:
        del ACTIVE_TESTS[test_id_int]

    return result_summary

@app.post("/result")
async def result_detail(request: Request):
    user_id = get_current_user_id(request)
    data = await request.json()
    test_id = data.get("test_id")
    
    conn = get_db_connection()
    t = conn.execute("SELECT * FROM history WHERE user_id = ? AND id = ?", (user_id, test_id)).fetchone()
    conn.close()
    
    if not t:
        raise HTTPException(status_code=404, detail="Test results not found")
        
    return {
        "test_id": t["id"],
        "subject": t["subject"],
        "score": t["score"],
        "total": t["total"],
        "percentage": t["percentage"],
        "correct": t["score"],
        "wrong": t["total"] - t["score"],
        "skipped": 0,
        "grade": t["grade"],
        "time_taken": t["time_taken"],
        "accuracy": t["accuracy"],
        "weak_topics": t["weak_topics"],
        "strong_topics": t["strong_topics"],
        "graded_details": json.loads(t["report_json"])
    }

@app.post("/study-plan")
async def generate_study_plan(request: Request):
    user_id = get_current_user_id(request)
    data = await request.json()
    report = data.get("report", {})
    subject = report.get("subject", "Embedded Systems")
    
    chapters = []
    for q in PYQ_INDEX:
        if q["subject"] == subject and q["section"] not in chapters:
            chapters.append(q["section"])
            
    if not chapters:
        chapters = ["Chapter 1: Foundations", "Chapter 2: Core Topics", "Chapter 3: Advanced Review"]
        
    plan = []
    topics_per_day = max(2, len(chapters) // 3)
    for i in range(3):
        day_chaps = chapters[i * topics_per_day : (i + 1) * topics_per_day]
        if i == 2:
            day_chaps = chapters[i * topics_per_day :]
        if not day_chaps:
            continue
        plan.append({
            "day": f"Day {i+1}",
            "topics": day_chaps,
            "hours": 4,
            "completion": 100
        })
        
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
        (user_id, f"New personalized study plan generated for {subject}.", "Study Reminder")
    )
    conn.commit()
    conn.close()
    
    return {
        "subject": subject,
        "plan": plan,
        "hours_needed": len(plan) * 4,
        "estimated_completion": "3 Days",
        "progress": 0
    }

@app.get("/history")
async def get_history(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    
    pdf_rows = conn.execute("SELECT filename, questions_count, report_json FROM history WHERE user_id = ? AND type = 'pdf_analysis' ORDER BY created_at DESC", (user_id,)).fetchall()
    test_rows = conn.execute("SELECT id, subject, score, total, percentage, grade, time_taken, accuracy, weak_topics, strong_topics FROM history WHERE user_id = ? AND type = 'mcq_test' ORDER BY created_at DESC", (user_id,)).fetchall()
    
    total_pdfs = len(pdf_rows)
    q_analyzed = sum(r["questions_count"] for r in pdf_rows)
    mcqs_attempted = len(test_rows)
    
    avg_score = round(sum(t["score"] for t in test_rows) / mcqs_attempted, 1) if mcqs_attempted > 0 else 0.0
    
    stats_row = conn.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    
    weak_counts = {}
    for t in test_rows:
         w = (t["weak_topics"] or "").split(", ")
         for item in w:
             if item and item != "None":
                 weak_counts[item] = weak_counts.get(item, 0) + 1
    weak_chaps = ", ".join(sorted(weak_counts, key=weak_counts.get, reverse=True)[:2])
    if not weak_chaps:
         weak_chaps = "None"
         
    analysis_history = []
    for r in pdf_rows:
        try:
            report = json.loads(r["report_json"])
        except:
            report = {}
        analysis_history.append({
            "filename": r["filename"],
            "questions_count": r["questions_count"],
            "report": report
        })
        
    test_history = []
    for t in test_rows:
        test_history.append({
            "test_id": t["id"],
            "subject": t["subject"],
            "score": t["score"],
            "total": t["total"],
            "percentage": t["percentage"],
            "grade": t["grade"]
        })
        
    study_progress_pct = min(100, total_pdfs * 20 + mcqs_attempted * 10)
    
    conn.execute(
        "UPDATE user_stats SET completed_tasks = ?, remaining_tasks = ?, study_hours = ?, completed_chapters = ? WHERE user_id = ?",
        (mcqs_attempted, max(0, 5 - mcqs_attempted), round(total_pdfs * 1.5 + mcqs_attempted * 0.5, 1), len(pdf_rows), user_id)
    )
    conn.commit()
    
    stats_row = conn.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    
    return {
        "analysis_history": analysis_history,
        "test_history": test_history,
        "dashboard_stats": {
            "uploaded_pdfs": total_pdfs,
            "questions_analyzed": q_analyzed,
            "mcqs_attempted": mcqs_attempted,
            "avg_score": f"{avg_score} / 20" if mcqs_attempted > 0 else "0 / 20",
            "avg_score_raw": avg_score,
            "high_priority_completed": stats_row["high_priority_left"] if stats_row else 0,
            "weak_chapters": weak_chaps,
            "study_progress": f"{study_progress_pct}%"
        },
        "user_stats": dict(stats_row) if stats_row else {}
    }

def extract_questions_from_pdf(file_bytes):
    import io
    import re
    questions = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            raw_lines = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                lines = page_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 1. Skip page numbers (lines that are just digits, or "Page X of Y", or "- X -")
                    if re.match(r'^[\-\s]*\d+[\-\s]*$', line):
                        continue
                    if re.match(r'^(page|pg\.?)\s*\d+', line, re.IGNORECASE):
                        continue
                    # 2. Skip obvious repeated titles / headers / course code stamps
                    if "semester" in line.lower() or "examination" in line.lower() or "subject code" in line.lower():
                        continue
                    if "seat no" in line.lower() or "enrolment no" in line.lower():
                        continue
                    
                    raw_lines.append(line)
            
            # Now, merge wrapped lines into complete questions!
            accumulated_questions = []
            current_q = []
            
            # Delimiters indicating a new question/sub-question starts
            new_q_pattern = r'^(?:Q(?:uestion)?\.?\s*[-_]?\s*\d+|\(?[a-zA-Z0-9]+\)?\s*[\)\.]|\[[a-zA-Z0-9]\])'
            
            for line in raw_lines:
                # Split on new question indicator
                if re.match(new_q_pattern, line, re.IGNORECASE):
                    if current_q:
                        accumulated_questions.append(" ".join(current_q))
                        current_q = []
                current_q.append(line)
                
            if current_q:
                accumulated_questions.append(" ".join(current_q))
                
            # Now, clean each accumulated question:
            for q_text in accumulated_questions:
                cleaned = q_text.strip()
                # Run recursive prefix cleanup loop to clean Q.3, (a), [b], 1. etc.
                while True:
                    m = re.match(r'^(?:Q(?:uestion)?\.?\s*[-_]?\s*\d+|\(?[a-zA-Z0-9]+\)?\s*[\)\.]|\[[a-zA-Z0-9]\]|or)\s*', cleaned, re.IGNORECASE)
                    if not m:
                        break
                    cleaned = cleaned[m.end():].strip()

                # Remove marks stamps like [7 Marks], (3 marks), [07], (7)
                cleaned = re.sub(r'\[\s*\d+\s*\]|\(\s*\d+\s*\)|\\[\s*\d+\s*marks\s*\\]|\(\s*\d+\s*marks\s*\)', '', cleaned, flags=re.IGNORECASE)
                
                # Clean up multiple whitespaces
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                
                if len(cleaned) > 15:
                    questions.append(cleaned)
                    
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        
    if not questions:
        questions = [
            "Define and classify Embedded Systems, and list examples of such systems.",
            "Compare Wi-Fi, Bluetooth and Zigbee protocols.",
            "Derive the expression for the radiation resistance of half-wave dipole.",
            "Explain Watchdog Timer, Real Time Clock and Brown Out Reset.",
            "Discuss the design process in embedded systems with examples."
        ]
    return questions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
