/* # NEW FILE */
(() => {
  const payload = document.getElementById("chartPayload");
  if (!payload || typeof Chart === "undefined") return;

  const labels = JSON.parse(payload.dataset.labels || "[]");
  const totals = JSON.parse(payload.dataset.totals || "[]");
  const electricity = JSON.parse(payload.dataset.electricity || "[]");
  const water = JSON.parse(payload.dataset.water || "[]");
  const telecom = JSON.parse(payload.dataset.telecom || "[]");
  const pvaLabels = JSON.parse(payload.dataset.pvaLabels || "[]");
  const pvaActual = JSON.parse(payload.dataset.pvaActual || "[]");
  const pvaPredicted = JSON.parse(payload.dataset.pvaPredicted || "[]");

  const trendEl = document.getElementById("trendChart");
  if (trendEl) {
    new Chart(trendEl, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Total", data: totals, borderColor: "#4f46e5", tension: 0.35 },
          { label: "Electricity", data: electricity, borderColor: "#f97316", tension: 0.35 },
          { label: "Water", data: water, borderColor: "#0ea5e9", tension: 0.35 },
          { label: "Telecom", data: telecom, borderColor: "#10b981", tension: 0.35 },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  const categoryEl = document.getElementById("categoryChart");
  if (categoryEl && electricity.length) {
    const i = electricity.length - 1;
    new Chart(categoryEl, {
      type: "doughnut",
      data: {
        labels: ["Electricity", "Water", "Telecom"],
        datasets: [{
          data: [electricity[i] || 0, water[i] || 0, telecom[i] || 0],
          backgroundColor: ["#f97316", "#0ea5e9", "#10b981"],
        }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  const compareEl = document.getElementById("predictionComparisonChart");
  if (compareEl && pvaLabels.length) {
    new Chart(compareEl, {
      type: "bar",
      data: {
        labels: pvaLabels,
        datasets: [
          { label: "Actual", data: pvaActual, backgroundColor: "#a5b4fc" },
          { label: "Predicted", data: pvaPredicted, backgroundColor: "#4f46e5" },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }
})();
