// The Pandora Box — front-end renderer.
// Reads static JSON under /data/daily/ (populated by the daily Claude Code
// agent — see AUTOMATION.md) and the static pattern library below, and
// renders them client-side. No build step required.

const ARCHITECTURE_LIBRARY = [
  {
    name: "Prompt Chaining",
    tags: ["workflow", "decomposition"],
    blurb: "Split a task into an ordered sequence of LLM calls, each working on the previous step's output. Trades latency for accuracy on tasks that decompose cleanly into fixed subtasks."
  },
  {
    name: "Routing",
    tags: ["workflow", "classification"],
    blurb: "Classify an input first, then dispatch it to a specialized prompt, model, or tool path. Keeps simple cases cheap and lets hard cases get a bigger model or more context."
  },
  {
    name: "Parallelization",
    tags: ["workflow", "throughput"],
    blurb: "Run independent subtasks concurrently (sectioning) or run the same task multiple times and vote/aggregate (voting). Useful when subtasks don't depend on each other's output."
  },
  {
    name: "Orchestrator–Workers",
    tags: ["multi-agent", "delegation"],
    blurb: "A central orchestrator dynamically breaks a task into subtasks and delegates to worker LLMs, then synthesizes their results. Unlike static parallelization, the subtask list isn't known in advance."
  },
  {
    name: "Evaluator–Optimizer",
    tags: ["self-critique", "quality"],
    blurb: "One LLM call generates a response; another evaluates it against explicit criteria and returns feedback, looping until the evaluator is satisfied. Effective when quality is hard to specify up front but easy to critique."
  },
  {
    name: "ReAct (Reason + Act)",
    tags: ["reasoning", "tool-use"],
    blurb: "Interleave explicit reasoning traces with tool calls, feeding each observation back into the next reasoning step. The foundation most tool-using single agents still build on."
  },
  {
    name: "Reflexion",
    tags: ["self-critique", "memory"],
    blurb: "An agent verbally critiques its own failed attempt, stores that reflection in episodic memory, and retries with the lesson in context — reinforcement learning without gradient updates."
  },
  {
    name: "Autonomous Agent Loop",
    tags: ["multi-agent", "autonomy"],
    blurb: "An LLM plans, acts via tools, and observes results in an open-ended loop, checking in with a human or ground-truth signal at the end rather than at each step. Powerful and unpredictable — needs guardrails."
  },
  {
    name: "Memory Architectures",
    tags: ["memory", "state"],
    blurb: "Episodic (what happened), semantic (what's true), and procedural (how to do things) memory, each with different retrieval and write strategies, layered to give an agent continuity across sessions."
  },
  {
    name: "Human-in-the-Loop Gates",
    tags: ["safety", "control"],
    blurb: "Insert mandatory approval checkpoints before irreversible or high-blast-radius actions (payments, deletions, external messages), independent of how autonomous the rest of the loop is."
  }
];

function renderLibrary() {
  const grid = document.getElementById("library-grid");
  grid.innerHTML = ARCHITECTURE_LIBRARY.map((p, i) => `
    <div class="pattern-card">
      <div class="pattern-num">${String(i + 1).padStart(2, "0")}</div>
      <h3>${escapeHtml(p.name)}</h3>
      <p>${escapeHtml(p.blurb)}</p>
      <div class="pattern-tags">${p.tags.map(t => `<span>${escapeHtml(t)}</span>`).join("")}</div>
    </div>
  `).join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(iso) {
  const d = new Date(iso + "T00:00:00Z");
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
}

async function loadDaily() {
  const todayCard = document.getElementById("today-card");
  const archiveList = document.getElementById("archive-list");

  try {
    const res = await fetch("data/daily/index.json", { cache: "no-store" });
    if (!res.ok) throw new Error("index.json not found");
    const index = await res.json();

    if (!index.length) {
      todayCard.innerHTML = `<p class="error">No entries yet — the box hasn't been opened.</p>`;
      archiveList.innerHTML = `<p class="error">Nothing in the archive yet.</p>`;
      return;
    }

    const sorted = [...index].sort((a, b) => b.date.localeCompare(a.date));
    document.getElementById("stat-entries").textContent = sorted.length;

    const latestMeta = sorted[0];
    const latestRes = await fetch(`data/daily/${latestMeta.file}`, { cache: "no-store" });
    const latest = await latestRes.json();
    todayCard.innerHTML = renderEntry(latest);

    archiveList.innerHTML = sorted.map(e => `
      <a class="archive-item" href="data/daily/${e.file}" target="_blank" rel="noopener">
        <span class="archive-date">${formatDate(e.date)}</span>
        <span class="archive-title">${escapeHtml(e.title)}</span>
        <span class="archive-pattern">${escapeHtml(e.pattern || "")}</span>
      </a>
    `).join("");
  } catch (err) {
    todayCard.innerHTML = `<p class="error">Couldn't load today's entry (${escapeHtml(err.message)}). If you're browsing this locally via file://, serve it over http instead — fetch() needs that.</p>`;
    archiveList.innerHTML = `<p class="error">Archive unavailable.</p>`;
  }
}

function renderEntry(entry) {
  const sources = (entry.sources || []).map(s =>
    `<a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">${escapeHtml(s.title)}</a>`
  ).join("");

  return `
    <div class="today-date">
      <span>${formatDate(entry.date)}</span>
      ${entry.pattern ? `<span class="today-pattern-tag">${escapeHtml(entry.pattern)}</span>` : ""}
    </div>
    <h3>${escapeHtml(entry.title)}</h3>
    <p class="summary">${escapeHtml(entry.summary)}</p>
    ${entry.key_learning ? `
      <div class="key-learning">
        <strong>Key learning</strong>
        ${escapeHtml(entry.key_learning)}
      </div>` : ""}
    ${sources ? `<div class="sources">${sources}</div>` : ""}
  `;
}

document.getElementById("year").textContent = new Date().getFullYear();
renderLibrary();
loadDaily();
