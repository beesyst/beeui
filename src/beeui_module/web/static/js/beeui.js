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

  function actionApiPath(name) {
    var body = document.body;
    var prefix = body ? body.getAttribute("data-beeui-route-prefix") || "" : "";
    return prefix + "/api/actions/" + name;
  }

  function csrfPath() {
    var body = document.body;
    var prefix = body ? body.getAttribute("data-beeui-route-prefix") || "" : "";
    return prefix + "/auth/csrf";
  }

  async function requestBoundedAction(name, body) {
    var csrfResponse = await fetch(csrfPath(), { credentials: "same-origin" });
    if (!csrfResponse.ok) throw new Error("CSRF request failed");
    var csrf = await csrfResponse.json();
    var headers = { "Content-Type": "application/json", "X-CSRF-Token": (csrf.data || {}).csrf_token || "" };
    var response = await fetch(actionApiPath(name), { method: "POST", credentials: "same-origin", headers: headers, body: JSON.stringify(body) });
    var data = await response.json().catch(function () { return {}; });
    if (!response.ok) throw new Error((data.error || {}).message || "Action request failed");
    return data;
  }

  function boundedActionMessage(error, fallback) {
    var message = error && typeof error.message === "string" ? error.message : fallback;
    return message.slice(0, 512);
  }

  function actionLabels() {
    return document.documentElement.lang.toLowerCase().indexOf("ru") === 0 ? {
      save: "Сохранить",
      cancel: "Отмена",
      refresh: "Действие выполнено, но таблицу не удалось обновить.",
      failed: "Не удалось выполнить действие."
    } : {
      save: "Save",
      cancel: "Cancel",
      refresh: "The action completed, but the table could not be refreshed.",
      failed: "The action could not be completed."
    };
  }

  function showTableActionError(source, text) {
    var container = source && source.closest(".beeui-live-table[data-beeui-table-id]");
    var target = container || (source && source.closest("td, form, .modal-content"));
    if (!target) return;
    var existing = target.querySelector("[data-beeui-action-error]");
    if (existing) existing.remove();
    var message = document.createElement("div");
    message.className = "alert alert-danger mt-2 mb-0 py-2";
    message.setAttribute("role", "alert");
    message.setAttribute("data-beeui-action-error", "");
    message.textContent = text.slice(0, 512);
    target.appendChild(message);
  }

  function refreshDirectActionTable(source) {
    var labels = actionLabels();
    var table = source && source.closest(".beeui-live-table[data-beeui-table-id]");
    if (!table) {
      showTableActionError(source, labels.refresh);
      return;
    }
    replaceLiveTable(table, new URL(window.location.href), true, function () {
      showTableActionError(table, labels.refresh);
    });
  }

  function showBoundedActionModal(action, source) {
    var isDirect = action.flow === "direct_execute";
    var isRussian = document.documentElement.lang.toLowerCase().indexOf("ru") === 0;
    var labels = isRussian ? {
      action: "Действие",
      close: "Закрыть",
      cancel: "Отмена",
      preview: "Предпросмотр",
      confirmation: "Подтвердить выполнение",
      execute: "Выполнить",
      previewed: "Предпросмотр готов. Подтвердите выполнение.",
      changed: "Данные изменены. Выполните предпросмотр снова.",
      saved: "Данные изменены."
    } : {
      action: "Action",
      close: "Close",
      cancel: "Cancel",
      preview: "Preview",
      confirmation: "Confirm execution",
      execute: "Execute",
      previewed: "Preview is ready. Confirm execution.",
      changed: "Input changed. Preview again before execution.",
      saved: "Data changed."
    };
    var root = document.createElement("div");
    root._beeuiActionSource = source || null;
    root.className = "modal modal-blur fade";
    root.tabIndex = -1;
    root.setAttribute("role", "dialog");
    root.innerHTML = '<div class="modal-dialog modal-dialog-centered" role="document"><div class="modal-content"><div class="modal-header"><h5 class="modal-title"></h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><form><div class="modal-body"><div class="text-secondary beeui-action-message"></div><label class="form-check beeui-action-confirmation d-none"><input class="form-check-input" type="checkbox"><span class="form-check-label"></span></label></div><div class="modal-footer"><button type="button" class="btn btn-link link-secondary" data-bs-dismiss="modal"></button><button type="submit" class="btn btn-secondary"></button><button type="button" class="btn btn-primary d-none" disabled></button></div></form></div></div>';
    root.querySelector(".modal-title").textContent = action.label || labels.action;
    root.querySelector(".btn-close").setAttribute("aria-label", labels.close);
    var form = root.querySelector("form");
    var body = root.querySelector(".modal-body");
    var message = root.querySelector(".beeui-action-message");
    var preview = form.querySelector('[type="submit"]');
    var execute = form.querySelector('.modal-footer .btn-primary');
    var confirmation = root.querySelector(".beeui-action-confirmation");
    var confirmationInput = confirmation.querySelector("input");
    var confirmationLabel = confirmation.querySelector("span");
    var description = action.description || "";
    var actionToken = action.action_id + "-" + String(Date.now()) + "-" + String(Math.random()).slice(2);
    var cancelButton = root.querySelector(".modal-footer [data-bs-dismiss=\"modal\"]");
    root.querySelector(".modal-footer [data-bs-dismiss=\"modal\"]").textContent = labels.cancel;
    preview.textContent = isDirect ? labels.execute : labels.preview;
    execute.textContent = labels.execute;
    if (isDirect) {
      cancelButton.className = "btn";
      preview.className = "btn btn-primary";
    }
    var fields = action.fields || [];
    if (description && fields.length) {
      var help = document.createElement("div");
      help.className = "form-text text-secondary mb-3";
      help.textContent = description;
      body.insertBefore(help, message);
    }
    fields.forEach(function (field) {
      var group = document.createElement("div");
      group.className = "mb-3";
      var label = document.createElement("label");
      label.className = "form-label";
      label.textContent = field.label || field.name;
      var input = document.createElement("input");
      var inputId = "beeui-action-" + actionToken + "-" + field.name;
      input.className = "form-control";
      input.id = inputId;
      input.name = field.name;
      input.type = field.type;
      input.maxLength = field.max_length;
      input.required = field.required;
      input.value = field.value || "";
      label.htmlFor = inputId;
      if (field.required) label.classList.add("required");
      group.appendChild(label);
      group.appendChild(input);
      body.insertBefore(group, message);
    });
    if (!fields.length) message.textContent = description;
    var previewPayload = null;
    function currentPayload() {
      var payload = Object.assign({}, action.args || {});
      fields.forEach(function (field) { payload[field.name] = form.elements[field.name].value; });
      return payload;
    }
    function invalidatePreview() {
      if (previewPayload === null) return;
      previewPayload = null;
      confirmationInput.checked = false;
      confirmation.classList.add("d-none");
      execute.classList.add("d-none");
      execute.disabled = true;
      message.textContent = labels.changed;
    }
    fields.forEach(function (field) {
      form.elements[field.name].addEventListener("input", invalidatePreview);
      form.elements[field.name].addEventListener("change", invalidatePreview);
    });
    confirmationInput.addEventListener("change", function () {
      execute.disabled = !confirmationInput.checked || previewPayload === null;
    });
    var modal = window.bootstrap && window.bootstrap.Modal ? new window.bootstrap.Modal(root) : null;
    var backdrop = null;
    var closed = false;
    function closeModal() {
      if (closed) return;
      closed = true;
      document.removeEventListener("keydown", closeOnEscape);
      if (modal) {
        modal.hide();
        return;
      }
      root.remove();
      if (backdrop) backdrop.remove();
      document.body.classList.remove("modal-open");
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") closeModal();
    }
    root.addEventListener("hidden.bs.modal", function () { root.remove(); });
    root.querySelectorAll('[data-bs-dismiss="modal"]').forEach(function (dismiss) {
      dismiss.addEventListener("click", closeModal);
    });
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;
      var payload = currentPayload();
      preview.disabled = true;
      if (isDirect) {
        requestBoundedAction("execute", { action_id: action.action_id, payload: payload }).then(function () {
          closeModal();
          refreshDirectActionTable(root._beeuiActionSource);
        }).catch(function (error) {
          message.textContent = boundedActionMessage(error, actionLabels().failed);
        }).finally(function () {
          preview.disabled = false;
        });
        return;
      }
      requestBoundedAction("preview", { action_id: action.action_id, payload: payload }).then(function (data) {
        previewPayload = JSON.stringify(payload);
        confirmationLabel.textContent = action.confirmation || labels.confirmation;
        confirmation.classList.remove("d-none");
        execute.classList.remove("d-none");
        message.textContent = labels.previewed;
      }).catch(function (error) {
        message.textContent = error.message;
      }).finally(function () {
        preview.disabled = false;
      });
    });
    execute.addEventListener("click", function () {
      var payload = currentPayload();
      if (!confirmationInput.checked || previewPayload !== JSON.stringify(payload)) return;
      execute.disabled = true;
      requestBoundedAction("execute", { action_id: action.action_id, payload: payload }).then(function () {
        window.location.reload();
      }).catch(function (error) {
        message.textContent = error.message;
        execute.disabled = false;
      });
    });
    document.body.appendChild(root);
    if (modal) {
      modal.show();
      return;
    }
    backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop fade show";
    backdrop.addEventListener("click", closeModal);
    document.body.appendChild(backdrop);
    document.body.classList.add("modal-open");
    root.style.display = "block";
    root.setAttribute("aria-modal", "true");
    root.classList.add("show");
    root.focus();
    document.addEventListener("keydown", closeOnEscape);
  }

  function appendActionIcon(button, icon) {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    svg.setAttribute("class", "icon");
    svg.setAttribute("width", "24");
    svg.setAttribute("height", "24");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    var paths = icon === "device-floppy" ? ["M6 3h11l3 3v15H4V3Z", "M8 3v6h8V3", "M8 21v-7h8v7"] : ["m6 6 12 12", "m18 6-12 12"];
    paths.forEach(function (d) {
      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      svg.appendChild(path);
    });
    button.appendChild(svg);
  }

  function iconButton(label, icon) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-action";
    button.setAttribute("aria-label", label);
    button.title = label;
    appendActionIcon(button, icon);
    return button;
  }

  function beginInlineEdit(button, action) {
    var row = button.closest("tr");
    if (!row || row.getAttribute("data-beeui-editing") === "true") return;
    var cells = {};
    (action.fields || []).forEach(function (field) {
      var cell = row.querySelector('[data-beeui-column-key="' + field.name + '"]');
      if (!cell) return;
      var input = document.createElement("input");
      input.className = "form-control form-control-sm";
      input.name = field.name;
      input.type = field.type;
      input.maxLength = field.max_length;
      input.required = field.required;
      input.value = field.value || "";
      cells[field.name] = { cell: cell, html: cell.cloneNode(true), input: input };
      cell.replaceChildren(input);
    });
    if (!Object.keys(cells).length) return;
    row.setAttribute("data-beeui-editing", "true");
    var actionCell = button.closest("td");
    var previous = actionCell.cloneNode(true);
    var controls = document.createElement("div");
    controls.className = "btn-actions flex-nowrap justify-content-end";
    var labels = actionLabels();
    var save = iconButton(labels.save, "device-floppy");
    var cancel = iconButton(labels.cancel, "x");
    controls.appendChild(save);
    controls.appendChild(cancel);
    actionCell.replaceChildren(controls);
    cancel.addEventListener("click", function () {
      Object.keys(cells).forEach(function (key) {
        cells[key].cell.replaceWith(cells[key].html);
      });
      actionCell.replaceWith(previous);
      row.removeAttribute("data-beeui-editing");
    });
    save.addEventListener("click", function () {
      var payload = Object.assign({}, action.args || {});
      var valid = true;
      Object.keys(cells).forEach(function (key) {
        var input = cells[key].input;
        if (!input.reportValidity()) valid = false;
        payload[key] = input.value;
      });
      if (!valid) return;
      save.disabled = true;
      cancel.disabled = true;
      requestBoundedAction("execute", { action_id: action.action_id, payload: payload }).then(function () {
        refreshDirectActionTable(row);
      }).catch(function (error) {
        var message = document.createElement("div");
        message.className = "form-text text-danger";
        message.textContent = boundedActionMessage(error, labels.failed);
        controls.appendChild(message);
        save.disabled = false;
        cancel.disabled = false;
      });
    });
  }

  document.addEventListener("click", function (event) {
    if (!(event.target instanceof Element)) return;
    var button = event.target.closest("[data-beeui-bounded-action]");
    if (!button) return;
    try {
      var action = JSON.parse(button.getAttribute("data-action") || "{}");
      if (action.flow === "direct_execute" && action.inline_edit) {
        beginInlineEdit(button, action);
        return;
      }
      if (action.flow === "direct_execute" && !(action.fields || []).length) {
        button.disabled = true;
        requestBoundedAction("execute", { action_id: action.action_id, payload: action.args || {} }).then(function () {
          refreshDirectActionTable(button);
        }).catch(function (error) {
          button.disabled = false;
          showTableActionError(button, boundedActionMessage(error, actionLabels().failed));
        });
        return;
      }
      showBoundedActionModal(action, button);
    } catch (_) { }
  });

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
        hadSearch: value.length >= 3,
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

  function buildTableFormUrl(form, table, resetPage, excludedName) {
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
    if (excludedName) {
      url.searchParams.delete(excludedName);
    }
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

  function replaceLiveTable(table, url, strict, onFailure) {
    if (!window.fetch || !window.DOMParser || !window.history) {
      if (strict) {
        if (typeof onFailure === "function") onFailure();
        return;
      }
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
      replacement = document.importNode(replacement, true);
      getTableState(replacement).hadSearch = state.hadSearch;
      if (typeof window.beeuiDestroyComponents === "function") {
        window.beeuiDestroyComponents(table);
      }
      table.replaceWith(replacement);
      window.history.replaceState({}, "", result.url.href);
      if (typeof window.beeuiInitComponents === "function") {
        window.beeuiInitComponents(replacement);
      }
    }).catch(function (error) {
      if (state.version !== version || (error && error.name === "AbortError")) return;
      if (strict) {
        if (typeof onFailure === "function") onFailure();
        return;
      }
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
    var resetSearch = false;
    if (query.length >= 3) {
      state.hadSearch = true;
    } else if (state.hadSearch) {
      state.hadSearch = false;
      resetSearch = true;
    } else {
      return;
    }
    var url = buildTableFormUrl(
      form,
      table,
      true,
      resetSearch ? input.name : null
    );
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

  var runtimeAssets = {};

  function scopeContains(scope, selector) {
    return scope instanceof Element && scope.matches(selector) || scope.querySelector(selector);
  }

  function staticPrefix() {
    var body = document.body;
    var value = body ? body.getAttribute("data-beeui-static-prefix") : null;
    return value && value.indexOf("/") === 0 ? value.replace(/\/$/, "") : "/static";
  }

  function loadRuntimeAsset(name, path, stylesheet) {
    if (runtimeAssets[name]) return runtimeAssets[name];
    runtimeAssets[name] = new Promise(function (resolve, reject) {
      var selector = stylesheet ? 'link[data-beeui-runtime="' + name + '"]' : 'script[data-beeui-runtime="' + name + '"]';
      var existing = document.querySelector(selector);
      if (existing) {
        if (stylesheet || existing.dataset.beeuiLoaded === "true" || (name === "apexcharts" && window.ApexCharts) || (name === "litepicker" && window.Litepicker)) resolve();
        else existing.addEventListener("load", resolve, { once: true });
        return;
      }
      var node = document.createElement(stylesheet ? "link" : "script");
      node.setAttribute("data-beeui-runtime", name);
      if (stylesheet) {
        node.rel = "stylesheet";
        node.href = path;
      } else {
        node.src = path;
        node.async = true;
      }
      node.addEventListener("load", function () {
        node.dataset.beeuiLoaded = "true";
        resolve();
      }, { once: true });
      node.addEventListener("error", reject, { once: true });
      document.head.appendChild(node);
    });
    return runtimeAssets[name];
  }

  function loadComponentAssets(scope) {
    var loads = [];
    var prefix = staticPrefix();
    if (scopeContains(scope, ".beeui-chart-container[data-chart-config-id]")) {
      loads.push(loadRuntimeAsset("apexcharts", prefix + "/vendor/apexcharts/apexcharts.min.js", false));
    }
    if (scopeContains(scope, ".beeui-datepicker, .beeui-dr-trigger")) {
      window.disableLitepickerStyles = true;
      loads.push(loadRuntimeAsset("litepicker-css", prefix + "/vendor/litepicker/litepicker.min.css", true));
      loads.push(loadRuntimeAsset("litepicker", prefix + "/vendor/litepicker/litepicker.min.js", false));
    }
    return Promise.all(loads);
  }

  function dateLocale() {
    return document.documentElement.lang === "ru" ? "ru-RU" : "en-US";
  }

  function dateLanguage() {
    return document.documentElement.lang === "ru" ? "ru" : "en";
  }

  var datePresetLabels = {
    today: { en: "Today", ru: "Сегодня" },
    yesterday: { en: "Yesterday", ru: "Вчера" },
    last_7: { en: "Last 7 days", ru: "7 дней" },
    last_30: { en: "Last 30 days", ru: "30 дней" }
  };

  function formatDate(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, "0");
    var day = String(date.getDate()).padStart(2, "0");
    return year + "-" + month + "-" + day;
  }

  function formatDateDisplay(from, to) {
    return from + " — " + to;
  }

  function dateColumns() {
    return window.innerWidth < 768 ? 1 : 2;
  }

  function submitDateForm(form) {
    if (!form) return;
    if (typeof form.requestSubmit === "function") form.requestSubmit();
    else form.submit();
  }

  function createDateRangePicker(pickerFactory, trigger, fromInput, toInput, input, restoreRange) {
    var fromValue = fromInput ? fromInput.value : "";
    var toValue = toInput ? toInput.value : "";
    var fromDate = fromValue ? new Date(fromValue + "T00:00:00") : null;
    var toDate = toValue ? new Date(toValue + "T00:00:00") : null;
    var suppressSubmit = false;
    var picker = new pickerFactory({
      element: input,
      format: "YYYY-MM-DD",
      singleMode: false,
      numberOfMonths: dateColumns(),
      numberOfColumns: dateColumns(),
      lang: dateLocale(),
      autoApply: true,
      startDate: fromDate || undefined,
      endDate: toDate || undefined,
      buttonText: {
        previousMonth: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-chevron-left" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M15 6l-6 6 6 6"/></svg>',
        nextMonth: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-chevron-right" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 6l6 6-6 6"/></svg>'
      },
      setup: function (instance) {
        instance.on("show", function () {
          var pickerRoot = instance.ui instanceof HTMLElement ? instance.ui : null;
          if (!pickerRoot || pickerRoot.querySelector(".beeui-dr-presets")) return;
          var presetsBar = document.createElement("div");
          presetsBar.className = "beeui-dr-presets d-flex gap-1 flex-wrap";
          [
            { key: "today", days: 0 },
            { key: "yesterday", days: 1 },
            { key: "last_7", days: 6 },
            { key: "last_30", days: 29 }
          ].forEach(function (preset) {
            var button = document.createElement("button");
            button.type = "button";
            button.textContent = datePresetLabels[preset.key][dateLanguage()];
            button.className = "btn btn-sm btn-outline-secondary beeui-dr-preset";
            button.setAttribute("data-preset", preset.key);
            button.addEventListener("click", function (event) {
              event.preventDefault();
              var today = new Date();
              today.setHours(0, 0, 0, 0);
              var from = new Date(today);
              var to = new Date(today);
              if (preset.key === "yesterday") {
                from.setDate(from.getDate() - 1);
                to = new Date(from);
              } else {
                from.setDate(from.getDate() - preset.days);
              }
              var selectedFrom = formatDate(from);
              var selectedTo = formatDate(to);
              if (fromInput) fromInput.value = selectedFrom;
              if (toInput) toInput.value = selectedTo;
              input.value = formatDateDisplay(selectedFrom, selectedTo);
              suppressSubmit = true;
              try { instance.setDateRange(from, to); } catch (_) { }
              suppressSubmit = false;
              submitDateForm(trigger.closest("form"));
            });
            presetsBar.appendChild(button);
          });
          pickerRoot.appendChild(presetsBar);
        });
        instance.on("selected", function (from, to) {
          if (suppressSubmit || !from) return;
          var selectedFrom = from.format ? from.format("YYYY-MM-DD") : formatDate(new Date(from));
          var selectedTo = to
            ? (to.format ? to.format("YYYY-MM-DD") : formatDate(new Date(to)))
            : selectedFrom;
          if (fromInput) fromInput.value = selectedFrom;
          if (toInput) toInput.value = selectedTo;
          input.value = formatDateDisplay(selectedFrom, selectedTo);
          if (to) submitDateForm(trigger.closest("form"));
        });
      }
    });
    if (restoreRange && fromDate) picker.setDateRange(fromDate, toDate || fromDate);
    return picker;
  }

  function initDatepickers(scope) {
    if (typeof window.Litepicker === "undefined") return;
    var pickerFactory = window.Litepicker.Litepicker || window.Litepicker.default || window.Litepicker;
    var target = scope || document;
    target.querySelectorAll(".beeui-dr-trigger").forEach(function (trigger) {
      if (trigger.dataset.beeuiDatepickerInitialized) return;
      var wrapper = trigger.closest(".beeui-table-toolbar-date-group");
      var input = trigger.querySelector(".beeui-dr-input");
      if (!wrapper || !input) return;
      var fromInput = wrapper.querySelector(".beeui-dr-from");
      var toInput = wrapper.querySelector(".beeui-dr-to");
      trigger.dataset.beeuiDatepickerInitialized = "true";
      var picker = createDateRangePicker(pickerFactory, trigger, fromInput, toInput, input, false);
      var resizeTimer = null;
      var resizeHandler = function () {
        if (resizeTimer) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          var oldColumns = picker && picker.options && picker.options.numberOfColumns;
          if (dateColumns() !== oldColumns && picker && typeof picker.destroy === "function") {
            picker.destroy();
            picker = createDateRangePicker(pickerFactory, trigger, fromInput, toInput, input, true);
          }
        }, 300);
      };
      window.addEventListener("resize", resizeHandler);
      trigger.beeuiDatepickerCleanup = function () {
        if (resizeTimer) clearTimeout(resizeTimer);
        window.removeEventListener("resize", resizeHandler);
        if (picker && typeof picker.destroy === "function") picker.destroy();
      };
    });
    target.querySelectorAll(".beeui-datepicker").forEach(function (input) {
      if (input.dataset.beeuiDatepickerInitialized) return;
      input.dataset.beeuiDatepickerInitialized = "true";
      var picker = new pickerFactory({
        element: input,
        format: "YYYY-MM-DD",
        singleMode: true,
        autoApply: true,
        resetButton: true,
        lang: dateLocale(),
        setup: function (instance) {
          instance.on("selected", function () { submitDateForm(input.closest("form")); });
          instance.on("clear:selection", function () { submitDateForm(input.closest("form")); });
        }
      });
      input.beeuiDatepickerCleanup = function () {
        if (picker && typeof picker.destroy === "function") picker.destroy();
      };
    });
  }

  function destroyDatepickers(scope) {
    var target = scope || document;
    target.querySelectorAll("[data-beeui-datepicker-initialized]").forEach(function (element) {
      if (typeof element.beeuiDatepickerCleanup === "function") element.beeuiDatepickerCleanup();
    });
  }

  function chartError(element, state) {
    element.textContent = "";
    var empty = document.createElement("div");
    empty.className = "empty";
    var title = document.createElement("div");
    title.className = "empty-title";
    var messageAttribute = state === "error"
      ? "data-chart-error-message"
      : "data-chart-unavailable-message";
    title.textContent = element.getAttribute(messageAttribute) || "";
    empty.appendChild(title);
    element.appendChild(empty);
  }

  function initCharts(scope) {
    if (typeof window.ApexCharts === "undefined") return;
    var target = scope || document;
    target.querySelectorAll(".beeui-chart-container[data-chart-config-id]").forEach(function (element) {
      if (element.dataset.beeuiChartInitialized) return;
      var configNode = document.getElementById(element.getAttribute("data-chart-config-id"));
      if (!configNode || configNode.type !== "application/json") {
        chartError(element, "unavailable");
        return;
      }
      try {
        var config = JSON.parse(configNode.textContent || "{}");
        config.chart = config.chart || {};
        config.chart.el = element;
        config.theme = config.theme || {};
        config.theme.mode = getEffectiveTheme() === "dark" ? "dark" : "light";
        var chart = new window.ApexCharts(element, config);
        element.dataset.beeuiChartInitialized = "true";
        element.beeuiChart = chart;
        var rendered = chart.render();
        if (rendered && typeof rendered.then === "function") {
          rendered.then(function () { window.beeuiRegisterChart(chart); }).catch(function () { chartError(element, "error"); });
        } else {
          window.beeuiRegisterChart(chart);
        }
      } catch (_) {
        chartError(element, "error");
      }
    });
  }

  function destroyCharts(scope) {
    var target = scope || document;
    target.querySelectorAll(".beeui-chart-container[data-beeui-chart-initialized]").forEach(function (element) {
      if (element.beeuiChart && typeof element.beeuiChart.destroy === "function") {
        try { element.beeuiChart.destroy(); } catch (_) { }
      }
      chartInstances = chartInstances.filter(function (chart) { return chart !== element.beeuiChart; });
    });
  }

  function initComponents(scope) {
    var target = scope || document;
    return loadComponentAssets(target).then(function () {
      initDatepickers(target);
      initCharts(target);
    }).catch(function () { });
  }

  function destroyComponents(scope) {
    destroyDatepickers(scope);
    destroyCharts(scope);
  }

  window.beeuiInitDatepickers = initDatepickers;
  window.beeuiDestroyDatepickers = destroyDatepickers;
  window.beeuiInitComponents = initComponents;
  window.beeuiDestroyComponents = destroyComponents;

  var pageTabState = { controller: null, version: 0 };

  function isSafePageTabUrl(url) {
    return url && url.origin === window.location.origin && url.protocol === window.location.protocol;
  }

  function findPageTabsSurface(documentNode, surfaceId) {
    var surfaces = documentNode.querySelectorAll("[data-beeui-page-tabs-surface]");
    for (var index = 0; index < surfaces.length; index += 1) {
      if (surfaces[index].getAttribute("data-beeui-page-tabs-surface") === surfaceId) return surfaces[index];
    }
    return null;
  }

  function cancelPageTabRequest() {
    pageTabState.version += 1;
    if (pageTabState.controller) pageTabState.controller.abort();
    pageTabState.controller = null;
  }

  function replacePageTabs(surface, url, historyMode) {
    if (!window.fetch || !window.DOMParser || !window.history || !isSafePageTabUrl(url)) {
      window.location.assign(url.href);
      return;
    }
    cancelPageTabRequest();
    var version = pageTabState.version;
    var controller = typeof AbortController === "function" ? new AbortController() : null;
    pageTabState.controller = controller;
    var options = { credentials: "same-origin", headers: { Accept: "text/html" } };
    if (controller) options.signal = controller.signal;
    window.fetch(url.href, options).then(function (response) {
      var responseUrl = new URL(response.url, window.location.href);
      if (!response.ok || !isSafePageTabUrl(responseUrl)) throw new Error("page_tabs_response");
      return response.text().then(function (html) { return { html: html, url: responseUrl }; });
    }).then(function (result) {
      if (pageTabState.version !== version) return;
      var documentNode = new DOMParser().parseFromString(result.html, "text/html");
      var surfaceId = surface.getAttribute("data-beeui-page-tabs-surface");
      var replacement = findPageTabsSurface(documentNode, surfaceId);
      if (!replacement || replacement.getAttribute("data-beeui-page-tabs-progressive") !== "true") throw new Error("page_tabs_identity");
      replacement.querySelectorAll('script:not(script[type="application/json"].beeui-chart-config)').forEach(function (script) { script.remove(); });
      replacement = document.importNode(replacement, true);
      destroyComponents(surface);
      surface.replaceWith(replacement);
      if (historyMode === "push") window.history.pushState({}, "", result.url.href);
      initComponents(replacement);
    }).catch(function (error) {
      if (pageTabState.version !== version || (error && error.name === "AbortError")) return;
      window.location.assign(url.href);
    });
  }

  document.addEventListener("click", function (event) {
    if (!(event.target instanceof Element)) return;
    var link = event.target.closest("a[data-beeui-page-tab]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var surface = link.closest("[data-beeui-page-tabs-surface][data-beeui-page-tabs-progressive=true]");
    var url = new URL(link.href, window.location.href);
    if (!surface || !isSafePageTabUrl(url)) return;
    event.preventDefault();
    replacePageTabs(surface, url, "push");
  });

  window.addEventListener("popstate", function () {
    var surface = document.querySelector("[data-beeui-page-tabs-surface][data-beeui-page-tabs-progressive=true]");
    if (surface) replacePageTabs(surface, new URL(window.location.href), "none");
  });

  initComponents(document);
})();
