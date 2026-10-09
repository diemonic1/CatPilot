# Веб-интерфейс окна CatPilot (HTML/CSS/JS). Лежит строками в Python-модуле,
# чтобы PyInstaller забирал его в сборку сам, без --add-data.
# Отдаётся локальным сервером окна (uiApp в CatPilot.py), редактор — Monaco из catpilot_monaco.py

INDEX_HTML = r'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>__CP_TITLE__</title>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" data-name="vs/editor/editor.main" href="/vs/editor/editor.main.css">
</head>
<body>
<header class="topbar">
  <div class="brand">
    <span class="brand-name" id="brandName">CatPilot</span>
    <span class="chip" id="versionChip"></span>
    <span class="chip" id="portChip"></span>
  </div>
  <div class="topbar-actions">
    <button class="btn" id="btnSettings" data-t="settings"></button>
    <button class="btn" id="btnLog" data-t="log"></button>
    <button class="btn" id="btnHide" data-t="hidetotray"></button>
    <button class="btn btn-danger-ghost" id="btnKill"></button>
    <button class="btn btn-save" id="btnSave"><span data-t="save"></span><span class="dirty-dot"></span><kbd>Ctrl+S</kbd></button>
  </div>
</header>

<div class="layout">
  <aside class="sidebar">
    <div class="search-box">
      <input id="search" type="search" autocomplete="off" spellcheck="false">
    </div>
    <div class="task-list" id="taskList"></div>
    <div class="sidebar-footer">
      <button class="btn btn-primary btn-block" id="btnAdd">+ <span data-t="addTask"></span></button>
    </div>
  </aside>

  <main class="workspace">
    <div class="empty" id="emptyView">
      <div class="empty-title" id="emptyTitle"></div>
    </div>

    <section class="task-view hidden" id="taskView">
      <div class="task-form">
        <div class="form-row">
          <div class="field grow">
            <label for="fName" data-t="Name" data-tip="nameTooltip"></label>
            <input id="fName" type="text" autocomplete="off" spellcheck="false">
          </div>
          <div class="field grow">
            <label for="fUrl" data-t="URL" data-tip="urlTooltip"></label>
            <div class="url-input">
              <span class="url-prefix" id="urlPrefix"></span>
              <input id="fUrl" type="text" autocomplete="off" spellcheck="false">
            </div>
          </div>
          <div class="task-actions">
            <button class="btn btn-run" id="btnRun">&#9654; <span data-t="run"></span></button>
            <button class="btn btn-danger-ghost" id="btnDelete" data-t="delete"></button>
          </div>
        </div>

        <div class="form-row">
          <div class="toggles">
            <label class="switch" data-tip="NotifyCheckboxTooltip"><input type="checkbox" id="fNotify"><span class="track"></span><span data-t="Notify"></span></label>
            <label class="switch" data-tip="ShowInTG_BOTTooltip"><input type="checkbox" id="fTg"><span class="track"></span><span data-t="ShowInTG_BOT"></span></label>
            <label class="switch" data-tip="ShowInTrayTooltip"><input type="checkbox" id="fTray"><span class="track"></span><span data-t="ShowInTray"></span></label>
          </div>
          <div class="keys" data-tip="buttonsTooltip">
            <span class="keys-label" data-t="buttons"></span>
            <select id="fB1"></select><span class="plus">+</span>
            <select id="fB2"></select><span class="plus">+</span>
            <select id="fB3"></select>
          </div>
        </div>
      </div>

      <div class="editor-header">
        <span data-t="VBSScript" data-tip="VBSScriptTooltip"></span>
        <span class="editor-hint" id="cursorInfo"></span>
      </div>
      <div class="editor-host" id="editor"></div>
    </section>
  </main>
</div>

<div class="modal-backdrop hidden" id="settingsModal">
  <div class="modal modal-wide">
    <div class="modal-header"><span data-t="settings"></span><button class="icon-btn" data-close>&#10005;</button></div>
    <div class="modal-body settings-body">
      <h3 data-t="GeneralSettings"></h3>
      <div class="settings-grid">
        <label data-t="language"></label>
        <select id="sLanguage"></select>

        <label data-tip="portTooltip">PORT</label>
        <input id="sPort" type="number" min="1" max="65535">

        <label data-t="notify" data-tip="notifyTooltip"></label>
        <label class="switch"><input type="checkbox" id="sNotify"><span class="track"></span></label>

        <label data-t="traySetting" data-tip="traySettingTooltip"></label>
        <label class="switch"><input type="checkbox" id="sTray"><span class="track"></span></label>

        <label data-t="RunAtStart" data-tip="AutoStart"></label>
        <label class="switch"><input type="checkbox" id="sAutoStart"><span class="track"></span></label>

        <label data-t="NotifyOnStart" data-tip="NotifyOnStartToolTip"></label>
        <label class="switch"><input type="checkbox" id="sNotifyOnStart"><span class="track"></span></label>
      </div>

      <h3 data-t="SettingsBot"></h3>
      <div class="settings-grid">
        <label data-tip="BOTtokenTooltip">BOT token</label>
        <div class="secret">
          <input id="sToken" type="password" autocomplete="off" spellcheck="false">
          <button class="icon-btn" id="btnShowToken" type="button">&#128065;</button>
        </div>

        <label data-t="AllowedTG_IDs" data-tip="AllowedTG_IDsTooltip"></label>
        <input id="sAllowed" type="text" autocomplete="off" spellcheck="false">
      </div>

      <h3 data-t="AdditionalSettings"></h3>
      <div class="settings-grid">
        <label data-t="CheckWorkURLLabel" data-tip="CheckWorkURLTooltip"></label>
        <input id="sCheckUrl" type="text" autocomplete="off" spellcheck="false">

        <label data-t="AdditionalURLLabel" data-tip="AdditionalURLTooltip"></label>
        <input id="sAdditionalUrl" type="text" autocomplete="off" spellcheck="false">
      </div>
    </div>
    <div class="modal-footer">
      <span class="restart-note" id="restartNote"></span>
      <button class="btn" data-close data-t="cancel"></button>
      <button class="btn btn-primary" id="btnSaveSettings" data-t="saveAll"></button>
    </div>
  </div>
</div>

<div class="modal-backdrop hidden" id="logModal">
  <div class="modal modal-wide">
    <div class="modal-header"><span data-t="log"></span><button class="icon-btn" data-close>&#10005;</button></div>
    <div class="modal-body log-body" id="logBody"></div>
    <div class="modal-footer">
      <button class="btn" id="btnRefreshLog" data-t="refresh"></button>
      <button class="btn btn-primary" data-close data-t="close"></button>
    </div>
  </div>
</div>

<div class="modal-backdrop hidden" id="confirmModal">
  <div class="modal modal-small">
    <div class="modal-body confirm-text" id="confirmText"></div>
    <div class="modal-footer">
      <button class="btn" id="confirmNo" data-t="cancel"></button>
      <button class="btn btn-danger" id="confirmYes">OK</button>
    </div>
  </div>
</div>

<div class="tooltip hidden" id="tooltip"></div>
<div class="toasts" id="toasts"></div>

<script>window.CP_TOKEN = "__CP_TOKEN__";</script>
<script src="/vs/loader.js"></script>
<script src="/app.js"></script>
</body>
</html>
'''

STYLE_CSS = r''':root {
  --bg: #1b1b1d;
  --panel: #232326;
  --panel-2: #2a2a2e;
  --border: #36363b;
  --text: #e6e6e9;
  --muted: #9a9aa3;
  --accent: #3b82f6;
  --accent-hover: #2f6fd6;
  --green: #2ea043;
  --green-hover: #278a39;
  --red: #e5484d;
  --red-hover: #c93c41;
  --yellow: #e5b84d;
  --radius: 8px;
  --font: "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font: 14px/1.4 var(--font);
  overflow: hidden;
  user-select: none;
}

input, select, textarea { user-select: text; }

.hidden { display: none !important; }

/* Top bar */
.topbar {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 14px 0 18px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
}

.brand { display: flex; align-items: center; gap: 8px; min-width: 0; }
.brand-name { font-size: 16px; font-weight: 600; letter-spacing: .2px; }

.chip {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
  white-space: nowrap;
}

.topbar-actions { display: flex; gap: 8px; align-items: center; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 32px;
  padding: 0 14px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--panel-2);
  color: var(--text);
  font: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: background .12s, border-color .12s, opacity .12s;
}

.btn:hover { background: #333338; }
.btn:active { transform: translateY(1px); }
.btn:disabled { opacity: .5; cursor: default; }
.btn-block { width: 100%; }

.btn-primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent-hover); }

.btn-danger { background: var(--red); border-color: var(--red); color: #fff; }
.btn-danger:hover { background: var(--red-hover); }

.btn-danger-ghost { color: #ff8a8d; }
.btn-danger-ghost:hover { background: rgba(229, 72, 77, .15); border-color: var(--red); }

.btn-run { color: #8be9a0; }
.btn-run:hover { background: rgba(46, 160, 67, .15); border-color: var(--green); }

.btn-save { background: var(--green); border-color: var(--green); color: #fff; }
.btn-save:hover { background: var(--green-hover); }
.btn-save.dirty { background: var(--red); border-color: var(--red); }
.btn-save.dirty:hover { background: var(--red-hover); }
.btn-save kbd { font: 11px var(--font); opacity: .7; }
.btn-save .dirty-dot { display: none; width: 7px; height: 7px; border-radius: 50%; background: #fff; }
.btn-save.dirty .dirty-dot { display: inline-block; }

.icon-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  font-size: 15px;
  cursor: pointer;
}
.icon-btn:hover { background: var(--panel-2); color: var(--text); }

/* Layout */
.layout { display: flex; height: calc(100% - 52px); }

.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--panel);
  border-right: 1px solid var(--border);
}

.search-box { padding: 12px; }

.task-list { flex: 1; overflow-y: auto; padding: 0 8px; }

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  margin-bottom: 2px;
  border-radius: var(--radius);
  cursor: pointer;
  border: 1px solid transparent;
}
.task-item:hover { background: var(--panel-2); }
.task-item.active { background: rgba(59, 130, 246, .16); border-color: rgba(59, 130, 246, .45); }

.task-number {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 6px;
  background: var(--panel-2);
  color: var(--muted);
  font-size: 12px;
}
.task-item.active .task-number { background: var(--accent); color: #fff; }

.task-text { flex: 1; min-width: 0; }
.task-name, .task-url { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-name { font-weight: 500; }
.task-url { color: var(--muted); font-size: 12px; font-family: Consolas, monospace; }

.task-badges { display: flex; gap: 4px; align-items: center; margin-top: 4px; }
.task-badges:not(:has(.badge:not(.hidden))) { display: none; }
.badge { font-size: 10px; line-height: 14px; padding: 0 5px; border-radius: 4px; background: var(--panel-2); color: var(--muted); cursor: help; }
.task-item.active .badge { background: rgba(255, 255, 255, .08); }
.task-dirty { width: 8px; height: 8px; flex-shrink: 0; border-radius: 50%; background: var(--yellow); }

.task-list-empty { color: var(--muted); padding: 16px 10px; text-align: center; }

.sidebar-footer { padding: 12px; border-top: 1px solid var(--border); }

/* Workspace */
.workspace { flex: 1; min-width: 0; display: flex; flex-direction: column; }

.empty { flex: 1; display: grid; place-items: center; color: var(--muted); }
.empty-title { font-size: 15px; }

.task-view { flex: 1; min-height: 0; display: flex; flex-direction: column; }

.task-form {
  padding: 14px 18px 10px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}

.form-row { display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap; }

.field { display: flex; flex-direction: column; gap: 5px; min-width: 200px; }
.field.grow { flex: 1; }
.field label, .keys-label { color: var(--muted); font-size: 12px; }

input[type=text], input[type=search], input[type=number], input[type=password], select {
  height: 34px;
  padding: 0 10px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font: inherit;
  outline: none;
  transition: border-color .12s, box-shadow .12s;
}
input:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(59, 130, 246, .2); }
input.invalid { border-color: var(--red); box-shadow: 0 0 0 3px rgba(229, 72, 77, .2); }

.search-box input { width: 100%; }

select { padding-right: 6px; cursor: pointer; }
select option { background: var(--panel); }

.url-input { display: flex; align-items: stretch; }
.url-prefix {
  display: flex;
  align-items: center;
  padding: 0 8px;
  border: 1px solid var(--border);
  border-right: none;
  border-radius: var(--radius) 0 0 var(--radius);
  background: var(--panel-2);
  color: var(--muted);
  font-family: Consolas, monospace;
  font-size: 12px;
  white-space: nowrap;
}
.url-input input { flex: 1; min-width: 0; border-radius: 0 var(--radius) var(--radius) 0; font-family: Consolas, monospace; }

.task-actions { display: flex; gap: 8px; }

.toggles { display: flex; gap: 18px; flex-wrap: wrap; margin-right: auto; }

.switch { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; }
.switch input { display: none; }
.switch .track {
  position: relative;
  width: 34px;
  height: 20px;
  border-radius: 999px;
  background: #45454c;
  transition: background .15s;
  flex-shrink: 0;
}
.switch .track::after {
  content: "";
  position: absolute;
  top: 3px;
  left: 3px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  transition: transform .15s;
}
.switch input:checked + .track { background: var(--accent); }
.switch input:checked + .track::after { transform: translateX(14px); }

.keys { display: flex; align-items: center; gap: 6px; }
.keys select { width: 120px; }
.plus { color: var(--muted); }

.editor-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 18px;
  color: var(--muted);
  font-size: 12px;
}

.editor-host { flex: 1; min-height: 0; margin: 0 10px 10px; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, .55);
  animation: fade .12s ease-out;
}

.modal {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 60px);
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, .5);
  animation: pop .14s ease-out;
}
.modal-wide { width: min(900px, calc(100vw - 60px)); }
.modal-small { width: min(440px, calc(100vw - 60px)); }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px 12px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 16px;
  font-weight: 600;
}

.modal-body { padding: 18px 20px; overflow-y: auto; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--border);
}

.settings-body h3 { margin: 4px 0 12px; font-size: 13px; color: var(--green); font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
.settings-body h3:not(:first-child) { margin-top: 22px; }

.settings-grid { display: grid; grid-template-columns: 300px 1fr; gap: 10px 16px; align-items: center; }
.settings-grid > label:nth-child(odd) { color: var(--text); }
.settings-grid select, .settings-grid input[type=number] { width: 200px; }

.secret { display: flex; gap: 6px; }
.secret input { flex: 1; }

.restart-note { margin-right: auto; color: #ff8a8d; font-size: 12px; }

.log-body { font-family: Consolas, monospace; font-size: 12.5px; height: 60vh; user-select: text; }
.log-line { padding: 3px 0; border-bottom: 1px solid rgba(255, 255, 255, .04); word-break: break-word; }
.log-time { color: var(--muted); }
.log-line.error { color: #ff8a8d; }

.confirm-text { font-size: 15px; padding: 24px 22px; }

/* Tooltip, toasts */
.tooltip {
  position: fixed;
  z-index: 100;
  max-width: 420px;
  padding: 8px 10px;
  border-radius: 6px;
  background: #101012;
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 12.5px;
  pointer-events: none;
  box-shadow: 0 6px 20px rgba(0, 0, 0, .4);
}

.toasts { position: fixed; right: 16px; bottom: 16px; z-index: 200; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
.toast {
  max-width: 460px;
  padding: 10px 14px;
  border-radius: var(--radius);
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  box-shadow: 0 6px 20px rgba(0, 0, 0, .4);
  animation: pop .14s ease-out;
}
.toast.ok { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
.toast.warn { border-left-color: var(--yellow); }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: #3a3a40; border-radius: 10px; border: 2px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: #4a4a52; background-clip: padding-box; border: 2px solid transparent; }
::-webkit-scrollbar-track { background: transparent; }

@keyframes fade { from { opacity: 0; } }
@keyframes pop { from { opacity: 0; transform: scale(.97); } }
'''

APP_JS = r'''"use strict";

const $ = id => document.getElementById(id);

const ui = {
  strings: {},
  buttons: [],
  settings: {},
  tasks: [],          // {uid, savedUrl, url, name, button1..3, notify, tgBOT, trayCommand, model}
  saved: {},          // uid -> снимок сохранённого состояния
  selected: null,
  editor: null,
  nextUid: 1,
  dirty: false,
};

// Тексты, которых может не быть в старых файлах локализации
const FALLBACK = {
  search: "Search",
  noTasks: "No tasks yet",
  selectTask: "Select a task on the left or create a new one",
  saved: "Saved",
  cancel: "Cancel",
  close: "Close",
  refresh: "Refresh",
  unsavedCloseQ: "There are unsaved changes. Close the window without saving?",
  unsavedSettingsQ: "Unsaved task changes will be lost after the restart. Continue?",
  runSavedVersion: "The task has unsaved changes: the saved version is being run",
  notSavedYet: "Save the task first",
  connectionLost: "No connection to CatPilot",
  restarting: "Restarting...",
  tagNotifyTooltip: "Shows a notification when the script runs",
  tagTrayTooltip: "Shown in the tray menu",
  tagTgTooltip: "Shown in the Telegram bot command list",
  tagKeysTooltip: "Presses keys after the script runs",
};

function T(key) {
  return ui.strings[key] || FALLBACK[key] || key;
}

// ---------- API ----------

async function api(method, path, body) {
  let response;
  try {
    response = await fetch("/api" + path, {
      method,
      headers: { "X-CatPilot-Token": window.CP_TOKEN, "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (e) {
    toast(T("connectionLost"), "error");
    throw e;
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || response.statusText);
    error.data = data;
    throw error;
  }
  return data;
}

// ---------- Toasts, tooltip, modals ----------

function toast(text, kind = "info", timeout = 4000) {
  const el = document.createElement("div");
  el.className = "toast " + kind;
  el.textContent = text;
  $("toasts").appendChild(el);
  setTimeout(() => el.remove(), timeout);
}

function setupTooltips() {
  const tip = $("tooltip");
  document.addEventListener("mouseover", e => {
    const target = e.target.closest("[data-tip]");
    if (!target) { tip.classList.add("hidden"); return; }
    tip.textContent = T(target.dataset.tip);
    tip.classList.remove("hidden");
  });
  document.addEventListener("mousemove", e => {
    if (tip.classList.contains("hidden")) return;
    const x = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
    const y = e.clientY + 18 + tip.offsetHeight > window.innerHeight ? e.clientY - tip.offsetHeight - 10 : e.clientY + 18;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  });
}

function openModal(id) { $(id).classList.remove("hidden"); }
function closeModal(id) { $(id).classList.add("hidden"); }

function confirmDialog(text, okText) {
  return new Promise(resolve => {
    $("confirmText").textContent = text;
    $("confirmYes").textContent = okText || "OK";
    openModal("confirmModal");
    const done = result => {
      closeModal("confirmModal");
      $("confirmYes").onclick = $("confirmNo").onclick = null;
      resolve(result);
    };
    $("confirmYes").onclick = () => done(true);
    $("confirmNo").onclick = () => done(false);
  });
}

// ---------- Tasks state ----------

function snapshot(task) {
  return JSON.stringify([task.url, task.name, task.button1, task.button2, task.button3,
    task.notify, task.tgBOT, task.trayCommand, task.model.getValue()]);
}

function isTaskDirty(task) {
  return ui.saved[task.uid] !== snapshot(task);
}

function updateDirty() {
  const dirty = ui.tasks.some(isTaskDirty);
  ui.dirty = dirty;
  $("btnSave").classList.toggle("dirty", dirty);
  document.title = (dirty ? "* " : "") + document.title.replace(/^\* /, "");
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.setDirty(dirty, T("unsavedCloseQ"));
  }
}

function makeTask(data, savedUrl) {
  const task = {
    uid: ui.nextUid++,
    savedUrl,
    url: data.url,
    name: data.name,
    button1: data.button1 || "None",
    button2: data.button2 || "None",
    button3: data.button3 || "None",
    notify: data.notify || "True",
    tgBOT: data.tgBOT || "True",
    trayCommand: data.trayCommand || "True",
    model: monaco.editor.createModel(data.script || "", "vb"),
  };
  task.model.onDidChangeContent(() => { renderTaskItem(task); updateDirty(); });
  return task;
}

function markSaved(task) {
  task.savedUrl = task.url;
  ui.saved[task.uid] = snapshot(task);
}

function currentTask() {
  return ui.tasks.find(t => t.uid === ui.selected) || null;
}

// ---------- Rendering ----------

function renderTaskItem(task) {
  const el = document.querySelector(`.task-item[data-uid="${task.uid}"]`);
  if (!el) return;
  el.querySelector(".task-name").textContent = task.name || "—";
  el.querySelector(".task-url").textContent = "/" + task.url;
  el.querySelector(".task-dirty").classList.toggle("hidden", !isTaskDirty(task));
  el.querySelector(".badge-notify").classList.toggle("hidden", task.notify !== "True");
  el.querySelector(".badge-tray").classList.toggle("hidden", task.trayCommand !== "True");
  el.querySelector(".badge-tg").classList.toggle("hidden", task.tgBOT !== "True");
  el.querySelector(".badge-keys").classList.toggle("hidden", [task.button1, task.button2, task.button3].every(b => b === "None"));
}

function renderTaskList() {
  const list = $("taskList");
  const filter = $("search").value.trim().toLowerCase();
  list.innerHTML = "";

  ui.tasks.forEach((task, index) => {
    if (filter && !(task.name.toLowerCase().includes(filter) || task.url.toLowerCase().includes(filter))) return;

    const el = document.createElement("div");
    el.className = "task-item" + (task.uid === ui.selected ? " active" : "");
    el.dataset.uid = task.uid;
    el.innerHTML = `<div class="task-number"></div>
      <div class="task-text">
        <div class="task-name"></div>
        <div class="task-url"></div>
        <div class="task-badges">
          <span class="badge badge-notify" data-tip="tagNotifyTooltip">notify</span>
          <span class="badge badge-tray" data-tip="tagTrayTooltip">tray</span>
          <span class="badge badge-tg" data-tip="tagTgTooltip">tg</span>
          <span class="badge badge-keys" data-tip="tagKeysTooltip">keys</span>
        </div>
      </div>
      <span class="task-dirty"></span>`;
    el.querySelector(".task-number").textContent = index + 1;
    el.onclick = () => selectTask(task.uid);
    list.appendChild(el);
    renderTaskItem(task);
  });

  if (!ui.tasks.length) {
    const empty = document.createElement("div");
    empty.className = "task-list-empty";
    empty.textContent = T("noTasks");
    list.appendChild(empty);
  }
}

function fillTaskForm(task) {
  $("fName").value = task.name;
  $("fUrl").value = task.url;
  $("fUrl").classList.toggle("invalid", !/^[a-zA-Z0-9]+$/.test(task.url));
  $("fNotify").checked = task.notify === "True";
  $("fTg").checked = task.tgBOT === "True";
  $("fTray").checked = task.trayCommand === "True";
  $("fB1").value = task.button1;
  $("fB2").value = task.button2;
  $("fB3").value = task.button3;
}

function selectTask(uid) {
  ui.selected = uid;
  const task = currentTask();

  $("emptyView").classList.toggle("hidden", !!task);
  $("taskView").classList.toggle("hidden", !task);

  document.querySelectorAll(".task-item").forEach(el => el.classList.toggle("active", Number(el.dataset.uid) === uid));

  if (!task) return;

  fillTaskForm(task);
  ui.editor.setModel(task.model);
  requestAnimationFrame(() => { ui.editor.layout(); ui.editor.focus(); });
}

function applyStrings() {
  document.querySelectorAll("[data-t]").forEach(el => { el.textContent = T(el.dataset.t); });
  $("btnKill").textContent = T("kill") + " " + ui.program;
  $("search").placeholder = T("search");
  $("emptyTitle").textContent = T("selectTask");
  $("restartNote").textContent = T("afterSave1") + " " + ui.program + " " + T("afterSave2");
}

// ---------- Actions ----------

function bindTaskForm() {
  const bindText = (id, key, after) => $(id).addEventListener("input", () => {
    const task = currentTask();
    if (!task) return;
    task[key] = $(id).value;
    if (after) after(task);
    renderTaskItem(task);
    updateDirty();
  });

  bindText("fName", "name");
  bindText("fUrl", "url", () => $("fUrl").classList.toggle("invalid", !/^[a-zA-Z0-9]+$/.test($("fUrl").value)));

  const bindValue = (id, key, read) => $(id).addEventListener("change", () => {
    const task = currentTask();
    if (!task) return;
    task[key] = read($(id));
    renderTaskItem(task);
    updateDirty();
  });

  bindValue("fNotify", "notify", el => el.checked ? "True" : "False");
  bindValue("fTg", "tgBOT", el => el.checked ? "True" : "False");
  bindValue("fTray", "trayCommand", el => el.checked ? "True" : "False");
  bindValue("fB1", "button1", el => el.value);
  bindValue("fB2", "button2", el => el.value);
  bindValue("fB3", "button3", el => el.value);
}

function uniqueValue(base, key) {
  let value = base, n = 1;
  while (ui.tasks.some(t => t[key] === value)) value = base + (++n);
  return value;
}

function addTask() {
  const task = makeTask({
    url: uniqueValue("Test", "url"),
    name: uniqueValue("Test", "name"),
    script: 'Dim WShell\nSet WShell = CreateObject("WScript.Shell")\n\nWShell.Run("notepad.exe")\n',
  }, null);
  ui.tasks.push(task);
  $("search").value = "";
  renderTaskList();
  selectTask(task.uid);
  updateDirty();
  $("fName").focus();
  $("fName").select();
}

async function saveTasks() {
  const payload = ui.tasks.map(t => ({
    url: t.url, name: t.name, script: t.model.getValue(),
    button1: t.button1, button2: t.button2, button3: t.button3,
    notify: t.notify, tgBOT: t.tgBOT, trayCommand: t.trayCommand,
  }));

  try {
    await api("PUT", "/tasks", { tasks: payload });
  } catch (e) {
    if (e.data && e.data.error) {
      toast(e.data.error, "error", 6000);
      const task = ui.tasks[e.data.index];
      if (task) { $("search").value = ""; renderTaskList(); selectTask(task.uid); }
    }
    return false;
  }

  ui.tasks.forEach(markSaved);
  renderTaskList();
  updateDirty();
  toast(T("saved"), "ok", 2000);
  return true;
}

async function deleteTask() {
  const task = currentTask();
  if (!task) return;
  if (!await confirmDialog(T("DeleteTaskQ"), T("delete"))) return;

  if (task.savedUrl) {
    try { await api("DELETE", "/tasks/" + encodeURIComponent(task.savedUrl)); } catch (e) { return; }
  }

  const index = ui.tasks.indexOf(task);
  ui.tasks.splice(index, 1);
  delete ui.saved[task.uid];
  task.model.dispose();

  const next = ui.tasks[Math.min(index, ui.tasks.length - 1)];
  renderTaskList();
  selectTask(next ? next.uid : null);
  updateDirty();
}

async function runTask() {
  const task = currentTask();
  if (!task) return;
  if (!task.savedUrl) { toast(T("notSavedYet"), "warn"); return; }
  if (isTaskDirty(task)) toast(T("runSavedVersion"), "warn");

  try {
    const result = await api("POST", "/run/" + encodeURIComponent(task.savedUrl));
    toast(result.message, result.message.includes(T("success")) ? "ok" : "error");
  } catch (e) { /* toast уже показан */ }
}

async function hideToTray() {
  if (ui.dirty && !await confirmDialog(T("unsavedCloseQ"), T("close"))) return;
  if (window.pywebview && window.pywebview.api) window.pywebview.api.close();
  else window.close();
}

async function killProgram() {
  if (ui.dirty && !await confirmDialog(T("unsavedCloseQ"), T("kill"))) return;
  await api("POST", "/quit").catch(() => {});
}

// ---------- Settings, log ----------

function openSettings() {
  const s = ui.settings;
  const languages = $("sLanguage");
  languages.innerHTML = "";
  ui.languages.forEach(lang => languages.add(new Option(lang, lang)));
  languages.value = s.language;

  $("sPort").value = s.PORT;
  $("sNotify").checked = s.showNotifications === "True";
  $("sTray").checked = s.closeToTrayOnStart === "True";
  $("sAutoStart").checked = s.AutoStart === "True";
  $("sNotifyOnStart").checked = s.NotifyOnStart === "True";
  $("sToken").value = s.TG_TOKEN || "";
  $("sToken").type = "password";
  $("sAllowed").value = s.AllowedTG_IDs || "";
  $("sCheckUrl").value = s.CheckWorkURL || "";
  $("sAdditionalUrl").value = s.AdditionalURL || "";
  openModal("settingsModal");
}

async function saveSettings() {
  if (ui.dirty && !await confirmDialog(T("unsavedSettingsQ"), T("saveAll"))) return;

  const flag = id => $(id).checked ? "True" : "False";
  const settings = {
    PORT: $("sPort").value,
    language: $("sLanguage").value,
    showNotifications: flag("sNotify"),
    closeToTrayOnStart: flag("sTray"),
    AutoStart: flag("sAutoStart"),
    NotifyOnStart: flag("sNotifyOnStart"),
    TG_TOKEN: $("sToken").value,
    AllowedTG_IDs: $("sAllowed").value,
    CheckWorkURL: $("sCheckUrl").value,
    AdditionalURL: $("sAdditionalUrl").value,
  };

  try {
    await api("PUT", "/settings", settings);
  } catch (e) {
    if (e.data && e.data.error) toast(e.data.error, "error");
    return;
  }

  // CatPilot перезапустится и сам откроет новое окно
  ui.dirty = false;
  if (window.pywebview && window.pywebview.api) window.pywebview.api.setDirty(false, "");
  $("btnSaveSettings").disabled = true;
  toast(T("restarting"), "info", 10000);
}

async function openLog() {
  openModal("logModal");
  await refreshLog();
}

async function refreshLog() {
  let data;
  try { data = await api("GET", "/log"); } catch (e) { return; }

  const body = $("logBody");
  body.innerHTML = "";
  data.lines.forEach(line => {
    if (!line.trim()) return;
    const el = document.createElement("div");
    el.className = "log-line" + (line.includes("ERROR") ? " error" : "");
    const split = line.indexOf(" | ");
    const time = document.createElement("span");
    time.className = "log-time";
    time.textContent = split >= 0 ? line.slice(0, split + 3) : "";
    el.appendChild(time);
    el.appendChild(document.createTextNode(split >= 0 ? line.slice(split + 3) : line));
    body.appendChild(el);
  });
}

// ---------- Monaco ----------

function setupMonaco() {
  monaco.editor.defineTheme("catpilot", {
    base: "vs-dark",
    inherit: true,
    rules: [{ token: "comment", foreground: "6A9955", fontStyle: "italic" }],
    colors: { "editor.background": "#1b1b1d", "editorGutter.background": "#1b1b1d" },
  });

  const snippet = (label, insertText, documentation) => ({ label, insertText, documentation });
  const snippets = [
    snippet("shell", 'Dim WShell\nSet WShell = CreateObject("WScript.Shell")\n$0', "WScript.Shell"),
    snippet("WShell.Run", 'WShell.Run "${1:notepad.exe}", ${2:1}, ${3:False}', "Run a program: command, window style, wait"),
    snippet("WShell.SendKeys", 'WShell.SendKeys "${1:{ENTER\\}}"', "Send keystrokes to the active window"),
    snippet("WShell.AppActivate", 'WShell.AppActivate "${1:Window title}"', "Activate a window by title"),
    snippet("WScript.Sleep", "WScript.Sleep ${1:1000}", "Pause, milliseconds"),
    snippet("MsgBox", 'MsgBox "${1:text}"', "Message box"),
    snippet("If", "If ${1:condition} Then\n\t$0\nEnd If", "If ... Then"),
    snippet("For", "For ${1:i} = ${2:1} To ${3:10}\n\t$0\nNext", "For ... Next"),
  ];

  monaco.languages.registerCompletionItemProvider("vb", {
    provideCompletionItems(model, position) {
      const word = model.getWordUntilPosition(position);
      const range = { startLineNumber: position.lineNumber, endLineNumber: position.lineNumber, startColumn: word.startColumn, endColumn: word.endColumn };
      return {
        suggestions: snippets.map(s => ({
          label: s.label,
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: s.insertText,
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: s.documentation,
          range,
        })),
      };
    },
  });

  ui.editor = monaco.editor.create($("editor"), {
    theme: "catpilot",
    automaticLayout: true,
    fontFamily: "Cascadia Code, Consolas, monospace",
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    smoothScrolling: true,
    cursorSmoothCaretAnimation: "on",
    renderWhitespace: "selection",
    tabSize: 4,
    padding: { top: 10 },
  });

  ui.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => saveTasks());
  ui.editor.onDidChangeCursorPosition(e => {
    $("cursorInfo").textContent = `Ln ${e.position.lineNumber}, Col ${e.position.column}`;
  });
}

// ---------- Start ----------

async function start() {
  const state = await api("GET", "/state");

  ui.program = state.program;
  ui.strings = state.strings;
  ui.buttons = state.buttons;
  ui.languages = state.languages;
  ui.settings = state.settings;

  $("brandName").textContent = state.program;
  $("versionChip").textContent = "v" + state.version;
  $("portChip").textContent = "PORT " + state.port;
  $("urlPrefix").textContent = ":" + state.port + "/";
  applyStrings();

  ["fB1", "fB2", "fB3"].forEach(id => ui.buttons.forEach(b => $(id).add(new Option(b === " " ? "space ( )" : b, b))));

  setupMonaco();

  state.tasks.forEach(data => {
    const task = makeTask(data, data.url);
    ui.tasks.push(task);
    markSaved(task);
  });

  renderTaskList();
  selectTask(ui.tasks.length ? ui.tasks[0].uid : null);
  updateDirty();
}

function setupEvents() {
  $("btnSave").onclick = saveTasks;
  $("btnAdd").onclick = addTask;
  $("btnRun").onclick = runTask;
  $("btnDelete").onclick = deleteTask;
  $("btnSettings").onclick = openSettings;
  $("btnLog").onclick = openLog;
  $("btnRefreshLog").onclick = refreshLog;
  $("btnHide").onclick = hideToTray;
  $("btnKill").onclick = killProgram;
  $("btnSaveSettings").onclick = saveSettings;
  $("btnShowToken").onclick = () => { $("sToken").type = $("sToken").type === "password" ? "text" : "password"; };
  $("search").addEventListener("input", renderTaskList);

  document.querySelectorAll("[data-close]").forEach(el => {
    el.onclick = () => closeModal(el.closest(".modal-backdrop").id);
  });

  document.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.code === "KeyS") {
      e.preventDefault();
      saveTasks();
    } else if (e.key === "Escape") {
      if (!$("confirmModal").classList.contains("hidden")) $("confirmNo").click();
      else ["settingsModal", "logModal"].forEach(closeModal);
    }
  });

  // pywebview может подключить API позже загрузки страницы
  window.addEventListener("pywebviewready", updateDirty);

  bindTaskForm();
  setupTooltips();
}

window.MonacoEnvironment = { getWorkerUrl: () => "/vs/base/worker/workerMain.js" };
require.config({ paths: { vs: "/vs" } });

setupEvents();
require(["vs/editor/editor.main"], () => {
  start().catch(e => toast(String(e.message || e), "error", 10000));
});
'''
