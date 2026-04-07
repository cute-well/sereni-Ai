const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const typingIndicator = document.getElementById("typingIndicator");
const emergencyButtons = document.querySelectorAll(".emergency-btn");

const modal = document.getElementById("groundModal");
const closeModal = document.getElementById("closeModal");
const groundPrompt = document.getElementById("groundPrompt");
const groundForm = document.getElementById("groundForm");
const groundInput = document.getElementById("groundInput");
const responseList = document.getElementById("responseList");
const stepBadge = document.getElementById("stepBadge");
const motivationBox = document.getElementById("motivationBox");
const groundSuccess = document.getElementById("groundSuccess");

const API_BASE = "/api";

function appendMessage(text, role = "bot") {
  const bubble = document.createElement("div");
  bubble.className = `message ${role} fade-in`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendMeta(meta) {
  const m = document.createElement("div");
  m.className = "meta";
  m.textContent = meta;
  chatWindow.appendChild(m);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setTyping(show) {
  typingIndicator.style.display = show ? "inline-flex" : "none";
}

async function sendMessage(text) {
  setTyping(true);
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, user_id: "demo" })
    });
    const data = await res.json();
    setTyping(false);

    if (!res.ok) {
      appendMessage(data.error || "Something went wrong", "bot");
      return;
    }

    appendMessage(data.response, "bot");
    const polarity = data.sentiment?.compound ?? 0;
    const risk = data.risk?.level ?? "unknown";
    appendMeta(`Sentiment: ${polarity.toFixed(3)} | Risk: ${risk} | Confidence: ${data.confidence?.confidence ?? 0}`);

    if (data.response.toLowerCase().includes("grounding")) {
      openModal();
    }
  } catch (err) {
    console.error(err);
    setTyping(false);
    appendMessage("Network error. Please try again.", "bot");
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  messageInput.value = "";
  sendMessage(text);
});

// Emergency dropdowns
emergencyButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.getAttribute("data-target");
    const panel = document.getElementById(targetId);
    const isOpen = panel.classList.contains("open");

    document.querySelectorAll(".emergency-dropdown").forEach((p) => {
      p.classList.remove("open");
      p.setAttribute("aria-hidden", "true");
    });
    if (!isOpen) {
      panel.classList.add("open");
      panel.setAttribute("aria-hidden", "false");
    }
  });
});

// Grounding modal logic
const steps = [
  { prompt: "Name five things you can see.", expected: 5 },
  { prompt: "Name four things you can touch.", expected: 4 },
  { prompt: "Name three things you can hear.", expected: 3 },
  { prompt: "Name two things you can smell.", expected: 2 },
  { prompt: "Name one thing you can taste.", expected: 1 },
];
let currentStep = 0;

function openModal() {
  modal.classList.add("active");
  modal.setAttribute("aria-hidden", "false");
  groundSuccess.hidden = true;
  groundInput.focus();
  updateStep();
}

function closeGroundModal() {
  modal.classList.remove("active");
  modal.setAttribute("aria-hidden", "true");
}

closeModal.addEventListener("click", closeGroundModal);
modal.addEventListener("click", (e) => {
  if (e.target === modal || e.target.classList.contains("modal-backdrop")) closeGroundModal();
});

groundForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const value = groundInput.value.trim();
  if (!value) return;
  const items = value.split(",").map((v) => v.trim()).filter(Boolean);
  renderResponse(items);
  groundInput.value = "";
  advanceStep();
});

function renderResponse(items) {
  const ul = document.createElement("ul");
  items.forEach((it) => {
    const li = document.createElement("li");
    li.textContent = it;
    ul.appendChild(li);
  });
  responseList.appendChild(ul);
  responseList.scrollTop = responseList.scrollHeight;
}

function updateStep() {
  const step = steps[currentStep];
  groundPrompt.textContent = step.prompt;
  stepBadge.textContent = `Step ${currentStep + 1} of ${steps.length}`;
  motivationBox.textContent = currentStep === 0
    ? "Take a slow breath. We'll notice your surroundings together."
    : "Great work. Keep breathing gently and notice the next senses.";
}

function advanceStep() {
  currentStep += 1;
  if (currentStep >= steps.length) {
    groundForm.setAttribute("aria-hidden", "true");
    groundForm.style.display = "none";
    responseList.style.display = "none";
    groundPrompt.textContent = "";
    stepBadge.textContent = "Completed";
    groundSuccess.hidden = false;
    return;
  }
  updateStep();
}

// Optional: expose a button in chat to open grounding
appendMessage("Hi, I'm Sereni. How are you feeling right now?", "bot");

// Keyboard accessibility
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("active")) {
    closeGroundModal();
  }
});
