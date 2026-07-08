// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
// Same-origin by default (Flask serves this page + /api/* from one app).
// If the frontend is ever hosted separately from the backend, set the full
// backend URL here instead, e.g. "https://your-api.vercel.app"
const API_BASE_URL = "";

// ---------------------------------------------------------------------------
// Elements
// ---------------------------------------------------------------------------
const modeButtons = document.querySelectorAll(".mode-btn");
const panelSingle = document.getElementById("panel-single");
const panelBatch = document.getElementById("panel-batch");

const questionInput = document.getElementById("question-input");
const checkBtn = document.getElementById("check-btn");
const singleHint = document.getElementById("single-hint");
const resultArea = document.getElementById("result-area");

const batchInput = document.getElementById("batch-input");
const batchBtn = document.getElementById("batch-btn");
const batchHint = document.getElementById("batch-hint");
const batchResultArea = document.getElementById("batch-result-area");
const batchTbody = document.getElementById("batch-tbody");

const statusLine = document.getElementById("status-line");
const footerStatus = document.getElementById("footer-status");

// ---------------------------------------------------------------------------
// Mode toggle
// ---------------------------------------------------------------------------
modeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    modeButtons.forEach((b) => {
      b.classList.remove("is-active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("is-active");
    btn.setAttribute("aria-selected", "true");

    const mode = btn.dataset.mode;
    panelSingle.hidden = mode !== "single";
    panelBatch.hidden = mode !== "batch";
  });
});

// ---------------------------------------------------------------------------
// Health check on load
// ---------------------------------------------------------------------------
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    const data = await res.json();
    if (data.status === "ok") {
      footerStatus.textContent = `Backend ready — ${data.pyq_topics_loaded} past-paper topics loaded`;
    } else {
      footerStatus.textContent = `Backend reported an error: ${data.model_error || "unknown"}`;
    }
  } catch (err) {
    footerStatus.textContent = "Can't reach the backend right now.";
  }
}
checkHealth();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function priorityClass(priority) {
  if (!priority) return "";
  return priority.toLowerCase();
}

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle("is-error", isError);
}

function stubRow(filled, total) {
  const stubs = [];
  for (let i = 0; i < total; i++) {
    stubs.push(`<div class="stub ${i < filled ? "filled" : ""}"></div>`);
  }
  return `<div class="stub-row">${stubs.join("")}</div>`;
}

function chipList(items) {
  if (!items || items.length === 0) return "<span class=\"hint\">None on record</span>";
  return `<div class="chips">${items.map((i) => `<span class="chip">${escapeHtml(i)}</span>`).join("")}</div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Render a single result
// ---------------------------------------------------------------------------
function renderResult(data) {
  const pClass = priorityClass(data.priority);

  if (data.source === "pyq_history") {
    const total = data.papers ? data.papers.length : 0;
    const repeated = data.times_repeated ? parseInt(data.times_repeated.split("/")[0], 10) : 0;
    const totalFromCount = data.times_repeated ? parseInt(data.times_repeated.split("/")[1], 10) : total;

    resultArea.innerHTML = `
      <div class="result-card">
        <div class="result-top">
          <div>
            <p class="result-topic">${escapeHtml(data.matched_topic)}</p>
            <p class="result-meta">${escapeHtml(data.subject || "")}${data.section ? " · " + escapeHtml(data.section) : ""}</p>
          </div>
          <div class="stamp ${pClass}">${escapeHtml(data.priority)}</div>
        </div>

        <div class="repeat-row">
          <div class="repeat-label">
            <span>Appeared in past papers</span>
            <span>${escapeHtml(data.times_repeated)} · ${data.repeat_percentage}%</span>
          </div>
          ${stubRow(repeated, totalFromCount)}
        </div>

        <div class="chip-group">
          <p class="chip-group-label">Papers it showed up in</p>
          ${chipList(data.papers)}
        </div>

        <div class="chip-group">
          <p class="chip-group-label">Marks it has carried</p>
          ${chipList(data.marks)}
        </div>
      </div>
    `;
  } else {
    // ml_prediction fallback
    const confidenceRows = data.class_confidences
      ? Object.entries(data.class_confidences)
          .sort((a, b) => b[1] - a[1])
          .map(
            ([label, score]) => `
              <div class="confidence-row">
                <span>${escapeHtml(label)}</span>
                <div class="confidence-track"><div class="confidence-fill" style="width:${Math.round(score * 100)}%"></div></div>
                <span>${Math.round(score * 100)}%</span>
              </div>`
          )
          .join("")
      : "";

    resultArea.innerHTML = `
      <div class="result-card no-match-card">
        <div class="result-top">
          <div>
            <p class="result-topic">No exact match in past papers</p>
            <p class="result-meta">AI estimate</p>
          </div>
          <div class="stamp ${pClass}">${escapeHtml(data.priority)}</div>
        </div>

        <div class="estimate-note">
          <p>${escapeHtml(data.note || "This question hasn't shown up in the recorded papers yet — priority is a model estimate, not a repeat count.")}</p>
          ${confidenceRows ? `<div class="confidence-bars">${confidenceRows}</div>` : ""}
        </div>
      </div>
    `;
  }

  resultArea.hidden = false;
}

// ---------------------------------------------------------------------------
// Single question submit
// ---------------------------------------------------------------------------
async function submitQuestion() {
  const question = questionInput.value.trim();
  if (!question) {
    singleHint.textContent = "Type a question first.";
    singleHint.classList.add("is-error");
    return;
  }

  singleHint.classList.remove("is-error");
  singleHint.textContent = "Checking…";
  checkBtn.disabled = true;
  resultArea.hidden = true;
  setStatus("");

  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze-question`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();

    if (!res.ok) {
      singleHint.textContent = "";
      setStatus(data.error || "Something went wrong.", true);
      return;
    }

    singleHint.textContent = "";
    renderResult(data);
  } catch (err) {
    singleHint.textContent = "";
    setStatus("Couldn't reach the backend. Is it running?", true);
  } finally {
    checkBtn.disabled = false;
  }
}

checkBtn.addEventListener("click", submitQuestion);
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submitQuestion();
});

// ---------------------------------------------------------------------------
// Batch submit
// ---------------------------------------------------------------------------
async function submitBatch() {
  const lines = batchInput.value
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    batchHint.textContent = "Add at least one question, one per line.";
    batchHint.classList.add("is-error");
    return;
  }

  batchHint.classList.remove("is-error");
  batchHint.textContent = `Checking ${lines.length} question(s)…`;
  batchBtn.disabled = true;
  batchResultArea.hidden = true;
  setStatus("");

  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze-questions-batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questions: lines }),
    });
    const data = await res.json();

    if (!res.ok) {
      batchHint.textContent = "";
      setStatus(data.error || "Something went wrong.", true);
      return;
    }

    batchHint.textContent = "";
    renderBatch(data.results);
  } catch (err) {
    batchHint.textContent = "";
    setStatus("Couldn't reach the backend. Is it running?", true);
  } finally {
    batchBtn.disabled = false;
  }
}

function renderBatch(results) {
  batchTbody.innerHTML = results
    .map((r) => {
      const pClass = priorityClass(r.priority);
      return `
        <tr>
          <td>${escapeHtml(r.question)}</td>
          <td><span class="priority-tag ${pClass}">${escapeHtml(r.priority || "—")}</span></td>
          <td>${r.times_repeated ? escapeHtml(r.times_repeated) : "—"}</td>
          <td>${r.papers && r.papers.length ? escapeHtml(r.papers.join(", ")) : "—"}</td>
          <td>${r.marks && r.marks.length ? escapeHtml(r.marks.join(", ")) : "—"}</td>
          <td>${r.source === "pyq_history" ? "Past papers" : "AI estimate"}</td>
        </tr>
      `;
    })
    .join("");

  batchResultArea.hidden = false;
}

batchBtn.addEventListener("click", submitBatch);
