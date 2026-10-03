(() => {
  "use strict";
  const root = document.documentElement;
  const dialog = document.querySelector("#settings-dialog");
  const settings = {
    motion: localStorage.getItem("smc-motion") !== "false",
    largeText: localStorage.getItem("smc-large-text") === "true",
  };

  function applySettings() {
    root.classList.toggle("motion-off", !settings.motion);
    root.classList.toggle("large-text", settings.largeText);
    document.querySelectorAll("[data-setting]").forEach((input) => {
      input.checked = settings[input.dataset.setting];
    });
  }

  document.querySelector("[data-open-settings]")?.addEventListener("click", () => dialog.showModal());
  document.querySelectorAll("[data-setting]").forEach((input) => input.addEventListener("change", () => {
    settings[input.dataset.setting] = input.checked;
    localStorage.setItem(input.dataset.setting === "motion" ? "smc-motion" : "smc-large-text", String(input.checked));
    applySettings();
  }));

  document.querySelector("[data-copy-key]")?.addEventListener("click", async (event) => {
    await navigator.clipboard.writeText(document.querySelector("#transfer-key").textContent);
    event.currentTarget.textContent = event.currentTarget.dataset.copiedLabel;
    setTimeout(() => { event.currentTarget.textContent = event.currentTarget.dataset.copyLabel; }, 1600);
  });
  document.querySelector("[data-print]")?.addEventListener("click", () => window.print());

  // The encrypted packet lives after #, so it never appears in HTTP request logs.
  const packetField = document.querySelector("#packet");
  if (packetField && location.hash.startsWith("#packet=")) {
    packetField.value = decodeURIComponent(location.hash.slice(8));
    history.replaceState(null, "", location.pathname + location.search);
    document.querySelector('input[name="key"]')?.focus();
  }
  applySettings();
})();
