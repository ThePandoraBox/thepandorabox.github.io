// Shared helpers for generated entry/forecast/tag pages.
document.querySelectorAll(".js-year").forEach(el => {
  el.textContent = new Date().getFullYear();
});

document.querySelectorAll(".copy-link-btn").forEach(btn => {
  btn.addEventListener("click", async () => {
    const original = btn.textContent;
    try {
      await navigator.clipboard.writeText(window.location.href);
      btn.textContent = "Copied!";
    } catch (e) {
      btn.textContent = window.location.href;
    }
    setTimeout(() => { btn.textContent = original; }, 1500);
  });
});
