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

  var tableStates = new WeakMap();

  function getTableState(table) {
    var state = tableStates.get(table);
    if (!state) {
      var search = table.querySelector("[data-beeui-table-search]");
      var value = search ? search.value.trim() : "";
      state = {
        controller: null,
        timer: null,
        version: 0,
        renderedSearch: value,
        hadSearch: value !== "",
      };
      tableStates.set(table, state);
    }
    return state;
  }

  function cancelTableRequest(table) {
    var state = getTableState(table);
    state.version += 1;
    if (state.timer) {
      window.clearTimeout(state.timer);
      state.timer = null;
    }
    if (state.controller) {
      state.controller.abort();
      state.controller = null;
    }
  }

  function isSafeTableUrl(url) {
    return url && url.origin === window.location.origin && url.protocol === window.location.protocol;
  }

  function buildTableFormUrl(form, table, resetPage) {
    var url = new URL(form.action || window.location.href, window.location.href);
    if (!isSafeTableUrl(url)) return null;
    var data = new FormData(form);
    var names = [];
    data.forEach(function (_, name) {
      if (names.indexOf(name) === -1) names.push(name);
    });
    names.forEach(function (name) {
      url.searchParams.delete(name);
    });
    data.forEach(function (value, name) {
      if (typeof value === "string") url.searchParams.append(name, value);
    });
    if (resetPage) {
      url.searchParams.set(table.getAttribute("data-beeui-page-param") || "page", "1");
    }
    return url;
  }

  function findReplacementTable(documentNode, tableId) {
    var tables = documentNode.querySelectorAll("[data-beeui-table-id]");
    for (var index = 0; index < tables.length; index += 1) {
      if (tables[index].getAttribute("data-beeui-table-id") === tableId) return tables[index];
    }
    return null;
  }

  function replaceLiveTable(table, url) {
    if (!window.fetch || !window.DOMParser || !window.history) {
      window.location.assign(url.href);
      return;
    }
    cancelTableRequest(table);
    var state = getTableState(table);
    var version = state.version;
    var controller = typeof AbortController === "function" ? new AbortController() : null;
    state.controller = controller;
    var options = { credentials: "same-origin", headers: { Accept: "text/html" } };
    if (controller) options.signal = controller.signal;
    window.fetch(url.href, options).then(function (response) {
      if (!response.ok || !isSafeTableUrl(new URL(response.url, window.location.href))) {
        throw new Error("table_response");
      }
      return response.text().then(function (html) {
        return { html: html, url: new URL(response.url, window.location.href) };
      });
    }).then(function (result) {
      if (state.version !== version) return;
      var documentNode = new DOMParser().parseFromString(result.html, "text/html");
      var replacement = findReplacementTable(documentNode, table.getAttribute("data-beeui-table-id"));
      if (!replacement) throw new Error("table_identity");
      if (typeof window.beeuiDestroyDatepickers === "function") {
        window.beeuiDestroyDatepickers(table);
      }
      table.replaceWith(replacement);
      window.history.replaceState({}, "", result.url.href);
      if (typeof window.beeuiInitDatepickers === "function") {
        window.beeuiInitDatepickers(replacement);
      }
    }).catch(function (error) {
      if (state.version !== version || (error && error.name === "AbortError")) return;
      window.location.assign(url.href);
    });
  }

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    var table = form.closest(".beeui-live-table[data-beeui-table-id]");
    if (!table || form.method.toLowerCase() !== "get") return;
    var search = form.querySelector("[data-beeui-table-search]");
    var state = getTableState(table);
    var url = buildTableFormUrl(
      form,
      table,
      Boolean(search && search.value.trim() !== state.renderedSearch)
    );
    if (!url) return;
    event.preventDefault();
    replaceLiveTable(table, url);
  });

  document.addEventListener("input", function (event) {
    var input = event.target;
    if (!(input instanceof HTMLInputElement) || !input.hasAttribute("data-beeui-table-search")) return;
    var table = input.closest(".beeui-live-table[data-beeui-table-id]");
    var form = input.form;
    if (!table || !form) return;
    var state = getTableState(table);
    var query = input.value.trim();
    cancelTableRequest(table);
    if (!query && state.hadSearch) {
      state.hadSearch = false;
    } else if (query.length < 3) {
      return;
    } else {
      state.hadSearch = true;
    }
    var url = buildTableFormUrl(form, table, true);
    if (!url) return;
    state.timer = window.setTimeout(function () {
      state.timer = null;
      replaceLiveTable(table, url);
    }, 275);
  });

  document.addEventListener("change", function (event) {
      var select = event.target;
      if (!(select instanceof HTMLSelectElement)) return;
      var table = select.closest(".beeui-live-table[data-beeui-table-id]");

      if (select.hasAttribute("data-beeui-page-size-select")) {
        var option = select.options[select.selectedIndex];
        var pageSizeUrl = option ? new URL(option.value, window.location.href) : null;
        if (!isSafeTableUrl(pageSizeUrl)) return;
        if (table) replaceLiveTable(table, pageSizeUrl);
        else window.location.assign(pageSizeUrl.href);
        return;
      }

      if (select.hasAttribute("data-beeui-table-auto-submit") && select.form) {
        if (typeof select.form.requestSubmit === "function") select.form.requestSubmit();
        else select.form.submit();
      }
    });

  document.addEventListener("click", function (event) {
    if (!(event.target instanceof Element)) return;
    var link = event.target.closest("a[data-beeui-table-control]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var table = link.closest(".beeui-live-table[data-beeui-table-id]");
    var url = new URL(link.href, window.location.href);
    if (!table || !isSafeTableUrl(url)) return;
    event.preventDefault();
    replaceLiveTable(table, url);
  });
})();
