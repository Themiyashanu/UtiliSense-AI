/* # NEW FILE */
(() => {
  const forms = document.querySelectorAll(".needs-validation");
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });

  // Subtle reveal animation for cards
  const revealTargets = document.querySelectorAll(".ui-card, .metric-card, .hero-banner");
  revealTargets.forEach((el, idx) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(8px)";
    setTimeout(() => {
      el.style.transition = "opacity 280ms ease, transform 280ms ease";
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    }, 50 + idx * 35);
  });

  const billInputs = document.querySelectorAll(".bill-input");
  const billTotal = document.getElementById("billTotal");
  if (billInputs.length && billTotal) {
    const computeTotal = () => {
      if (billTotal.value !== "" && Number(billTotal.value) > 0) return;
      let total = 0;
      billInputs.forEach((input) => {
        total += Number(input.value || 0);
      });
      billTotal.value = total.toFixed(2);
    };
    billInputs.forEach((input) => input.addEventListener("input", computeTotal));
  }
})();
