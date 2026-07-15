(function () {
  "use strict";
  const root = document.documentElement;

  /* ─── Sidebar state sync ─── */
  (function initSidebar() {
    if (!root) return;
    root.setAttribute("data-beeui", "ready");

    const sidebar = document.getElementById("beeui-sidebar-menu");
    if (!sidebar) return;

    const syncSidebarState = function () {
      const isOpen = sidebar.classList.contains("show");
      root.setAttribute("data-beeui-sidebar", isOpen ? "open" : "closed");
    };

    syncSidebarState();
    sidebar.addEventListener("transitionend", syncSidebarState);
    sidebar.addEventListener("click", syncSidebarState);
  })();

  /* ─── Theme system ─── */
  function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function getStoredTheme() {
    try {
      return localStorage.getItem("beeui-theme");
    } catch (_) {
      return null;
    }
  }

  function setStoredTheme(mode) {
    try {
      if (mode === "auto") {
        localStorage.removeItem("beeui-theme");
      } else {
        localStorage.setItem("beeui-theme", mode);
      }
    } catch (_) { }
  }

  function getEffectiveTheme() {
    var stored = getStoredTheme();
    if (stored === "light" || stored === "dark") return stored;
    return getSystemTheme();
  }

  function setTheme(mode) {
    var effective = mode === "auto" ? getSystemTheme() : mode;
    root.setAttribute("data-bs-theme", effective);
    highlightActiveButton(mode || "auto");
  }

  function highlightActiveButton(mode) {
    var container = document.getElementById("beeui-theme-buttons");
    if (!container) return;
    var buttons = container.querySelectorAll(".beeui-theme-toggle-btn");
    buttons.forEach(function (btn) {
      var btnMode = btn.getAttribute("data-theme-mode");
      if (btnMode === mode) {
        btn.classList.add("is-active");
      } else {
        btn.classList.remove("is-active");
      }
    });
  }

  function initTheme() {
    var stored = getStoredTheme();
    setTheme(stored || "auto");

    /* Listen for system theme changes — only when no explicit choice stored */
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", function () {
        if (!getStoredTheme()) {
          setTheme("auto");
        }
      });
  }

  /* ─── Boot ─── */
  try { initTheme(); } catch (e) { console.error('beeui initTheme error:', e); }

  /* Expose setter for onclick in templates */
  window.beeuiSetTheme = function (mode) {
    setStoredTheme(mode);
    setTheme(mode);
  };
})();
