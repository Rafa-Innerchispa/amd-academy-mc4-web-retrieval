const form = document.querySelector("#query-form");
const query = document.querySelector("#query");
const url = document.querySelector("#url");
const run = document.querySelector("#run");
const clear = document.querySelector("#clear");
const statusBox = document.querySelector("#status");
const result = document.querySelector("#result");
const failure = document.querySelector("#failure");

const hide = (el) => el.classList.add("hidden");
const show = (el) => el.classList.remove("hidden");

clear.addEventListener("click", () => {
  form.reset();
  hide(statusBox);
  hide(result);
  hide(failure);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hide(result);
  hide(failure);
  show(statusBox);
  statusBox.textContent = "Navigating and verifying evidence…";
  run.disabled = true;

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
    const sourceKind = (data.metadata && data.metadata.candidate_source_kind) || "page";
    document.querySelector("#verification").textContent =
      data.verification_status + " · " + sourceKind;

    const p = data.provenance || {};
    const source = document.querySelector("#source");
    source.textContent = p.source_url || "";
    source.href = p.source_url || "#";
    document.querySelector("#evidence").textContent = p.verbatim_text || "";
    document.querySelector("#hash").textContent =
      p.snapshot_hash ? "SHA-256 " + p.snapshot_hash : "";

    const trail = document.querySelector("#trail");
    trail.innerHTML = "";
    (data.navigation_trail || []).forEach((step) => {
      const li = document.createElement("li");
      li.textContent = step.action + ": " + step.target_url;
      trail.appendChild(li);
    });

    hide(statusBox);
    show(result);
  } catch (err) {
    statusBox.textContent = "Error: " + err.message;
  } finally {
    run.disabled = false;
  }
});
