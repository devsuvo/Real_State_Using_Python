/* Crystal Bay Estates — dashboard behaviour */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const csrf = () => (document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/) || [])[1] || ($("input[name=csrfmiddlewaretoken]") || {}).value || "";

  /* Sidebar (mobile) */
  const sidebar = $("#dashSidebar");
  const overlay = $(".dash-overlay");
  const setSidebar = (open) => {
    if (!sidebar) return;
    sidebar.classList.toggle("is-open", open);
    if (overlay) overlay.classList.toggle("is-open", open);
  };
  $$("[data-sidebar-open]").forEach((b) => b.addEventListener("click", () => setSidebar(true)));
  $$("[data-sidebar-close]").forEach((b) => b.addEventListener("click", () => setSidebar(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setSidebar(false); });

  /* Alerts */
  $$(".dash-alert-close").forEach((b) => b.addEventListener("click", () => b.closest(".dash-alert").remove()));
  $$(".dash-alerts .dash-alert-success").forEach((a) => setTimeout(() => a.remove(), 6000));

  /* Auto-submit filters */
  $$("[data-autosubmit]").forEach((el) => el.addEventListener("change", () => el.form.submit()));

  /* Inline toggles in lists */
  $$("[data-toggle-url]").forEach((input) => {
    input.addEventListener("change", () => {
      input.disabled = true;
      fetch(input.dataset.toggleUrl, { method: "POST", headers: { "X-CSRFToken": csrf() }, credentials: "same-origin" })
        .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
        .then((d) => { input.checked = d.value; })
        .catch(() => { input.checked = !input.checked; alert("Could not save that change. Please try again."); })
        .finally(() => { input.disabled = false; });
    });
  });

  /* Bulk selection */
  const bulkForm = $("#bulkForm");
  if (bulkForm) {
    const bar = $(".bulk-bar", bulkForm);
    const boxes = () => $$("input[name=ids]", bulkForm);
    const refresh = () => {
      const n = boxes().filter((b) => b.checked).length;
      bar.hidden = n === 0;
      $("[data-bulk-count]", bar).textContent = n;
    };
    const all = $("[data-check-all]", bulkForm);
    if (all) all.addEventListener("change", () => { boxes().forEach((b) => { b.checked = all.checked; }); refresh(); });
    boxes().forEach((b) => b.addEventListener("change", refresh));
    bulkForm.addEventListener("submit", (e) => {
      const action = bulkForm.elements.action.value;
      if (action === "delete" && !confirm("Delete the selected items permanently?")) e.preventDefault();
    });
  }

  /* Image fields: live preview from file or URL */
  $$("[data-image-field]").forEach((wrap) => {
    const img = $("[data-preview-img]", wrap);
    const empty = $("[data-preview-empty]", wrap);
    const file = $("[data-file-input]", wrap);
    const url = $("[data-url-input]", wrap);
    const show = (src) => {
      if (!img) return;
      img.src = src || "";
      img.hidden = !src;
      if (empty) empty.hidden = !!src;
    };
    if (file) file.addEventListener("change", () => {
      const f = file.files && file.files[0];
      if (f) show(URL.createObjectURL(f));
    });
    if (url) url.addEventListener("input", () => {
      if (file && file.files && file.files.length) return;
      const v = url.value.trim();
      if (/^https?:\/\//.test(v)) show(v + (v.includes("unsplash") && !v.includes("&w=") ? "&w=640&q=70" : ""));
      else if (!v) show(img && img.dataset.initial ? img.dataset.initial : "");
    });
  });

  /* Icon fields: live preview */
  $$("[data-icon-input]").forEach((input) => {
    const preview = input.closest(".icon-input") && $("[data-icon-preview]", input.closest(".icon-input"));
    if (!preview) return;
    input.addEventListener("input", () => { preview.className = "bi " + (input.value.trim() || "bi-question"); });
  });

  /* Warn before leaving a form with unsaved changes */
  const form = $(".dash-form");
  if (form) {
    let dirty = false;
    form.addEventListener("input", () => { dirty = true; });
    form.addEventListener("change", () => { dirty = true; });
    form.addEventListener("submit", () => { dirty = false; });
    window.addEventListener("beforeunload", (e) => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
  }
})();
