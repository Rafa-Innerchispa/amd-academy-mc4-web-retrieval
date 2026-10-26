const form = document.querySelector("#query-form");
const query = document.querySelector("#query");
const url = document.querySelector("#url");
const run = document.querySelector("#run");
const clear = document.querySelector("#clear");
const statusBox = document.querySelector("#status");
const statusTitle = document.querySelector("#status-title");
const statusDetail = document.querySelector("#status-detail");
const statusTime = document.querySelector("#status-time");
const result = document.querySelector("#result");
const failure = document.querySelector("#failure");

const hide = (el) => el.classList.add("hidden");
const show = (el) => el.classList.remove("hidden");

const stages = [
  ["Understanding request", "Classifying the requested value and retrieval intent…"],
  ["Navigating source", "Following only bounded, relevant links…"],
  ["Extracting candidates", "Reading text, tables, JSON-LD and contact fields…"],
  ["Verifying evidence", "Rejecting anything that cannot be grounded to the source…"],
];

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    query.value = button.dataset.query || "";
    url.value = button.dataset.url || "";
    query.focus();
  });
});

clear.addEventListener("click", () => {
  form.reset();
  hide(statusBox);
  hide(result);
  hide(failure);
  document.querySelector("#trail").innerHTML = "";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hide(result);
  hide(failure);
  show(statusBox);
  run.disabled = true;

  const started = performance.now();
  let stage = 0;
  const paintStatus = () => {
    const elapsed = (performance.now() - started) / 1000;
    const targetStage = Math.min(stages.length - 1, Math.floor(elapsed / 0.65));
    if (targetStage !== stage) stage = targetStage;
    statusTitle.textContent = stages[stage][0];
    statusDetail.textContent = stages[stage][1];
    statusTime.textContent = elapsed.toFixed(1) + "s";
  };
  paintStatus();
  const ticker = setInterval(paintStatus, 90);

  try {
    const response = await fetch("/api/retrieve", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({query: query.value, url: url.value, max_hops: 5})
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || data.error || "Request failed");

    if (data.status !== "SUCCESS") {
      document.querySelector("#failure-reason").textContent =
        data.failure_reason || "No verifiable evidence was found within the navigation budget.";
      hide(statusBox);
      show(failure);
      return;
    }

    document.querySelector("#answer").textContent = data.answer || "—";
    const metadata = data.metadata || {};
    const sourceKind = metadata.candidate_source_kind || "page";
    document.querySelector("#verification").textContent =
      data.verification_status + " · " + sourceKind.replaceAll("_", " ");

    document.querySelector("#elapsed").textContent =
      metadata.elapsed_seconds != null ? Number(metadata.elapsed_seconds).toFixed(3) + "s" : "—";
    document.querySelector("#score").textContent =
      metadata.candidate_score != null ? Number(metadata.candidate_score).toFixed(2) : "—";
    document.querySelector("#steps").textContent = String((data.navigation_trail || []).length);

    const p = data.provenance || {};
    const source = document.querySelector("#source");
    source.textContent = p.source_url || "";
    source.href = p.source_url || "#";
    document.querySelector("#evidence").textContent = p.verbatim_text || "";
    document.querySelector("#hash").textContent =
      p.snapshot_hash ? p.snapshot_hash : "";

    const trail = document.querySelector("#trail");
    trail.innerHTML = "";
    (data.navigation_trail || []).forEach((step, index) => {
      const li = document.createElement("li");
      li.dataset.step = String(index + 1);
      li.textContent = step.action + " · " + step.target_url;
      trail.appendChild(li);
    });

    hide(statusBox);
    show(result);
    result.scrollIntoView({behavior: "smooth", block: "start"});
  } catch (err) {
    statusTitle.textContent = "Retrieval error";
    statusDetail.textContent = err.message;
  } finally {
    clearInterval(ticker);
    paintStatus();
    run.disabled = false;
  }
});
