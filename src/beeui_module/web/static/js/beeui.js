(function () {
  "use strict";
  const root = document.documentElement;

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

  function getSystemTheme() {
    return typeof window.matchMedia === "function" && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function getStoredTheme() {
    try {
      var mode = localStorage.getItem("beeui-theme");
      if (mode === "system" || mode === "light" || mode === "dark") return mode;
      if (mode) localStorage.removeItem("beeui-theme");
    } catch (_) {
    }
    return null;
  }

  function setStoredTheme(mode) {
    try {
      if (mode === "system" || mode === "light" || mode === "dark") {
        localStorage.setItem("beeui-theme", mode);
      }
    } catch (_) { }
  }

  function getConfiguredTheme() {
    var mode = root.getAttribute("data-beeui-theme-config");
    return mode === "light" || mode === "dark" || mode === "system" ? mode : "system";
  }

  function getSelectedTheme() {
    return getStoredTheme() || getConfiguredTheme();
  }

  function getEffectiveTheme() {
    var selected = getSelectedTheme();
    return selected === "system" ? getSystemTheme() : selected;
  }

  function setTheme(mode) {
    var effective = mode === "system" ? getSystemTheme() : mode;
    root.setAttribute("data-bs-theme", effective);
    highlightActiveButton(mode || "system");
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
    setTheme(getSelectedTheme());

    var media = typeof window.matchMedia === "function" ? window.matchMedia("(prefers-color-scheme: dark)") : null;
    if (media && typeof media.addEventListener === "function") media.addEventListener("change", function () {
        if (getSelectedTheme() === "system") {
          setTheme("system");
        }
      });
  }

  var chartInstances = [];

  window.beeuiRegisterChart = function (chart) {
    if (chart && typeof chart.updateOptions === 'function') {
      chartInstances.push(chart);
    }
  };

  function updateChartThemes() {
    var effective = getEffectiveTheme();
    var mode = effective === 'dark' ? 'dark' : 'light';
    chartInstances.forEach(function (chart) {
      try {
        chart.updateOptions({
          theme: { mode: mode },
        });
      } catch (_) {}
    });
  }

  var _origSetTheme = setTheme;
  setTheme = function (mode) {
    _origSetTheme(mode);
    try { updateChartThemes(); } catch (_) { }
  };

  try { initTheme(); } catch (e) { console.error('beeui initTheme error:', e); }

  window.beeuiSetTheme = function (mode) {
    if (mode === "system" || mode === "light" || mode === "dark") {
      setStoredTheme(mode);
      setTheme(mode);
    }
  };
})();
