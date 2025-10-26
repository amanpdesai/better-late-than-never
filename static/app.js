(() => {
  const form = document.getElementById("pipeline-form");
  const runButton = document.getElementById("run-button");
  const resultCard = document.getElementById("result-card");
  const runIdEl = document.getElementById("run-id");
  const statusFileEl = document.getElementById("status-file");
  const logsDirEl = document.getElementById("logs-dir");
  const commandEl = document.getElementById("command");
  const statusBlock = document.getElementById("status-block");
  const statusJsonEl = document.getElementById("status-json");

  let pollHandle = null;

  function gatherPayload() {
    const payload = {};
    const question = document.getElementById("question").value.trim();
    if (!question) {
      throw new Error("Question is required.");
    }
    payload.question = question;

    const startFrom = document.getElementById("start_from").value.trim();
    if (startFrom) {
      payload.start_from = startFrom;
    }

    const topK = document.getElementById("top_k").value;
    if (topK) {
      payload.top_k = Number(topK);
    }

    const model = document.getElementById("model").value.trim();
    if (model) {
      payload.model = model;
    }

    const randomCount = document.getElementById("random_count").value;
    if (randomCount) {
      payload.random_count = Number(randomCount);
    }

    const randomSeed = document.getElementById("random_seed").value;
    if (randomSeed) {
      payload.random_seed = Number(randomSeed);
    }

    if (document.getElementById("no_random_images").checked) {
      payload.no_random_images = true;
    }

    if (document.getElementById("dry_run").checked) {
      payload.dry_run = true;
    }

    return payload;
  }

  function setLoading(isLoading) {
    runButton.disabled = isLoading;
    runButton.textContent = isLoading ? "Launching..." : "Run pipeline";
  }

  function showResultCard(data) {
    resultCard.hidden = false;
    runIdEl.textContent = data.run_id;
    statusFileEl.textContent = data.status_file;
    logsDirEl.textContent = data.logs_dir;
    commandEl.textContent = data.command.join(" ");
    statusBlock.hidden = true;
    statusJsonEl.textContent = "";
  }

  function updateStatus(content) {
    statusBlock.hidden = false;
    statusJsonEl.textContent = content;
  }

  async function pollStatus(runId) {
    if (pollHandle) {
      clearInterval(pollHandle);
    }

    const poll = async () => {
      try {
        const res = await fetch(`/pipeline/status/${encodeURIComponent(runId)}`);
        if (res.status === 404) {
          updateStatus("Status file not created yet...");
          return;
        }
        if (!res.ok) {
          throw new Error(`Status request failed (${res.status})`);
        }
        const data = await res.json();
        updateStatus(JSON.stringify(data, null, 2));
        if (["completed", "failed"].includes((data.overall_status || "").toLowerCase())) {
          clearInterval(pollHandle);
          pollHandle = null;
        }
      } catch (err) {
        updateStatus(`Error fetching status: ${err.message}`);
        clearInterval(pollHandle);
        pollHandle = null;
      }
    };

    await poll();
    pollHandle = setInterval(poll, 3000);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (pollHandle) {
      clearInterval(pollHandle);
      pollHandle = null;
    }
    try {
      const payload = gatherPayload();
      setLoading(true);
      const response = await fetch("/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Request failed");
      }
      showResultCard(data);
      await pollStatus(data.run_id);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  });
})();
