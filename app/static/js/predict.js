/* # NEW FILE */
(() => {
  const btn = document.getElementById("btnPredict");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const apiUrl = btn.dataset.apiUrl;
    const result = document.getElementById("predictionResult");
    const errorBox = document.getElementById("predictionError");

    btn.disabled = true;
    btn.innerHTML = "Loading...";

    fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("predTotal").textContent = `LKR ${(data.total || 0).toLocaleString("en-LK")}`;
        document.getElementById("predElec").textContent = `LKR ${(data.electricity || 0).toLocaleString("en-LK")}`;
        document.getElementById("predWater").textContent = `LKR ${(data.water || 0).toLocaleString("en-LK")}`;
        document.getElementById("predTelecom").textContent = `LKR ${(data.telecom || 0).toLocaleString("en-LK")}`;
        document.getElementById("predConf").textContent = data.confidence || "-";
        result.style.display = "block";
        errorBox.style.display = "none";
      })
      .catch((err) => {
        errorBox.textContent = `Error: ${err.message}`;
        errorBox.style.display = "block";
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-cpu"></i> Get Prediction';
      });
  });
})();
