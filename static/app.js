/* ============================================================
   ShopEasy — Multi-Agent Support · frontend logic
   The browser owns the conversation + routing tallies; the
   server just routes one message at a time (POST /api/chat).
   ============================================================ */

const chat     = document.getElementById("chat");
const composer = document.getElementById("composer");
const input    = document.getElementById("input");
const sendBtn  = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");

const counts = { billing: 0, technical: 0, general: 0 };

const WELCOME_HTML = `
  <div class="welcome" id="welcome">
    <div class="welcome__icon">👋</div>
    <h3>Ask about billing, a technical issue, or an order.</h3>
    <p>Try one of these to watch the routing happen:</p>
    <div class="examples">
      <button class="example">I was charged twice for my order</button>
      <button class="example">I forgot my password and can't log in</button>
      <button class="example">Where is my order? It hasn't arrived yet</button>
      <button class="example">How do I cancel my ShopEasy Plus membership?</button>
    </div>
  </div>`;

/* ───────────────────────── Mode badge ───────────────────────── */
async function loadStatus() {
  const badge = document.getElementById("mode-badge");
  try {
    const res  = await fetch("/api/status");
    const data = await res.json();
    badge.classList.remove("mode--loading");
    if (data.live) {
      badge.classList.add("mode--live");
      document.getElementById("mode-label").textContent = "LIVE";
      document.getElementById("mode-sub").textContent   = data.model;
    } else {
      badge.classList.add("mode--mock");
      document.getElementById("mode-label").textContent = "MOCK";
      document.getElementById("mode-sub").textContent   = "offline canned answers";
    }
  } catch {
    badge.classList.remove("mode--loading");
    badge.classList.add("mode--mock");
    document.getElementById("mode-label").textContent = "Offline";
    document.getElementById("mode-sub").textContent   = "server not reachable";
  }
}

/* ───────────────────────── Rendering ───────────────────────── */
function dismissWelcome() {
  document.getElementById("welcome")?.remove();
}

function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function addUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg msg--user";
  row.innerHTML = `
    <div class="msg__avatar">🧑</div>
    <div class="msg__body">
      <div class="msg__meta">You</div>
      <div class="bubble"></div>
    </div>`;
  row.querySelector(".bubble").textContent = text; // textContent = safe from HTML injection
  chat.appendChild(row);
  scrollToBottom();
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "msg msg--general";
  row.id = "typing-row";
  row.innerHTML = `
    <div class="msg__avatar">🧭</div>
    <div class="msg__body">
      <div class="msg__meta">Router is thinking…</div>
      <div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>
    </div>`;
  chat.appendChild(row);
  scrollToBottom();
}

function addAssistantMessage({ category, agent_name, icon, reply }) {
  document.getElementById("typing-row")?.remove();

  const row = document.createElement("div");
  row.className = `msg msg--${category}`;
  row.innerHTML = `
    <div class="msg__avatar">${icon}</div>
    <div class="msg__body">
      <div class="msg__meta"></div>
      <div class="bubble"></div>
    </div>`;
  // Build the meta (name + category tag) without innerHTML so names stay safe.
  const meta = row.querySelector(".msg__meta");
  meta.textContent = agent_name;
  const tag = document.createElement("span");
  tag.className = `tag tag--${category}`;
  tag.textContent = category;
  meta.appendChild(tag);

  row.querySelector(".bubble").textContent = reply;
  chat.appendChild(row);
  scrollToBottom();
}

/* ───────────────────────── Analytics ───────────────────────── */
function updateAnalytics() {
  const total = counts.billing + counts.technical + counts.general;
  for (const cat of ["billing", "technical", "general"]) {
    document.getElementById(`count-${cat}`).textContent = counts[cat];
    const pct = total ? Math.round((counts[cat] / total) * 100) : 0;
    document.getElementById(`bar-${cat}`).style.width = pct + "%";
  }
  document.getElementById("total-note").textContent = total
    ? `${total} message${total !== 1 ? "s" : ""} handled.`
    : "No messages yet — ask something to see the routing.";
}

/* ───────────────────────── Send flow ───────────────────────── */
let busy = false;

async function sendMessage(text) {
  text = text.trim();
  if (busy || !text) return;
  busy = true;
  sendBtn.disabled = true;
  input.value = "";

  dismissWelcome();
  addUserMessage(text);
  addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    if (!res.ok) throw new Error("bad response");
    const data = await res.json();
    addAssistantMessage(data);
    if (counts[data.category] !== undefined) counts[data.category]++;
    updateAnalytics();
  } catch {
    document.getElementById("typing-row")?.remove();
    addAssistantMessage({
      category: "general",
      agent_name: "ShopEasy",
      icon: "⚠️",
      reply: "Sorry — I couldn't reach the server. Please make sure it's running and try again.",
    });
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

/* ───────────────────────── Events ───────────────────────── */
composer.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(input.value);
});

// Delegated: works for the initial welcome and any rebuilt one after a clear.
chat.addEventListener("click", (e) => {
  const btn = e.target.closest(".example");
  if (btn) sendMessage(btn.textContent);
});

clearBtn.addEventListener("click", () => {
  chat.innerHTML = WELCOME_HTML;
  counts.billing = counts.technical = counts.general = 0;
  updateAnalytics();
  input.focus();
});

/* ───────────────────────── Boot ───────────────────────── */
loadStatus();
updateAnalytics();
input.focus();
