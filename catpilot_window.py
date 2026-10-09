# Окно: управление процессом окна (CatPilot.exe --gui) и локальный API для него.
# API — отдельный сервер только для окна: слушает 127.0.0.1 на случайном порту и требует токен.
# Основной Flask (0.0.0.0) запускает задачу на любой /<page>, поэтому смешивать их нельзя
import ctypes
import os
import secrets
import subprocess
import threading
from contextlib import suppress

from flask import Flask, Response, abort, jsonify, request
from werkzeug.serving import make_server

from catpilot_config import PROGRAM_NAME, PROGRAM_VERSION, ParsePort, SaveSettings, settings
from catpilot_instance import AddShutdownHandler, GUI_ARG, QuitProgram, RestartProgram, SelfCommand
from catpilot_localization import CurrentLanguage, UiStrings, languagesList
from catpilot_log import ReadLogLines
from catpilot_tasks import BUTTONS, DeleteTaskFiles, LaunchWithoutConsole, LoadTasks, SaveTasks, StartTask

GUI_PORT_ENV = "CATPILOT_UI_PORT"
GUI_TOKEN_ENV = "CATPILOT_UI_TOKEN"

ASFW_ANY = -1
SW_RESTORE = 9

# Перезапуск/выход — после ответа, чтобы окно успело его получить
RESPONSE_DELAY = 0.3

UI_MIME_TYPES = {".js": "application/javascript", ".css": "text/css", ".ttf": "font/ttf", ".html": "text/html"}

guiProcess = None
guiLock = threading.Lock()
uiServerPort = 0
uiToken = secrets.token_urlsafe(24)
monacoArchive = None

#region Window process
def FindProcessWindow(pid):
    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, lparam):
        windowPid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd), ctypes.byref(windowPid))
        if windowPid.value == pid and user32.IsWindowVisible(ctypes.c_void_p(hwnd)):
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(callback, 0)
    return found[0] if found else None

def FocusProcessWindow(pid):
    hwnd = FindProcessWindow(pid)
    if hwnd is None:
        return

    user32 = ctypes.windll.user32
    if user32.IsIconic(ctypes.c_void_p(hwnd)):
        user32.ShowWindow(ctypes.c_void_p(hwnd), SW_RESTORE)
    user32.SetForegroundWindow(ctypes.c_void_p(hwnd))

def IsWindowOpen():
    return guiProcess is not None and guiProcess.poll() is None

def ShowWindow():
    global guiProcess

    with guiLock:
        if IsWindowOpen():
            FocusProcessWindow(guiProcess.pid)
            return

        # Разрешаем новому процессу забрать фокус (иначе окно может открыться под другими)
        with suppress(Exception):
            ctypes.windll.user32.AllowSetForegroundWindow(ASFW_ANY)

        env = dict(os.environ)
        env[GUI_PORT_ENV] = str(uiServerPort)
        env[GUI_TOKEN_ENV] = uiToken

        guiProcess = subprocess.Popen(SelfCommand(GUI_ARG), env=env, creationflags=subprocess.CREATE_NO_WINDOW)

def CloseWindow():
    with guiLock:
        if IsWindowOpen():
            with suppress(Exception):
                guiProcess.terminate()
#endregion

#region API
uiApp = Flask("CatPilotUI")

def UiResponse(content, mimetype, cache=False):
    response = Response(content, mimetype=mimetype)
    response.headers["Cache-Control"] = "max-age=86400" if cache else "no-store"
    return response

def JsonBody():
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        abort(400)
    return data

def ErrorResponse(text, status=400, **extra):
    return jsonify(dict(error=text, **extra)), status

@uiApp.before_request
def CheckUiToken():
    if request.path.startswith("/api/") and request.headers.get("X-CatPilot-Token") != uiToken:
        abort(403)

@uiApp.route("/")
def UiIndex():
    if request.args.get("token") != uiToken:
        abort(403)

    from catpilot_ui import INDEX_HTML
    return UiResponse(INDEX_HTML.replace("__CP_TOKEN__", uiToken).replace("__CP_TITLE__", PROGRAM_NAME + " | v" + PROGRAM_VERSION), "text/html")

@uiApp.route("/app.js")
def UiScript():
    from catpilot_ui import APP_JS
    return UiResponse(APP_JS, "application/javascript")

@uiApp.route("/style.css")
def UiStyle():
    from catpilot_ui import STYLE_CSS
    return UiResponse(STYLE_CSS, "text/css")

@uiApp.route("/vs/<path:path>")
def UiMonaco(path):
    global monacoArchive

    if monacoArchive is None:
        from catpilot_monaco import OpenMonacoArchive
        monacoArchive = OpenMonacoArchive()

    try:
        content = monacoArchive.read("vs/" + path)
    except KeyError:
        abort(404)

    return UiResponse(content, UI_MIME_TYPES.get(os.path.splitext(path)[1], "application/octet-stream"), cache=True)

@uiApp.route("/api/state")
def ApiState():
    return jsonify({
        "program": PROGRAM_NAME,
        "version": PROGRAM_VERSION,
        "port": settings["PORT"],
        "strings": UiStrings(),
        "languages": languagesList,
        "buttons": BUTTONS,
        "settings": settings,
        "tasks": LoadTasks(),
    })

@uiApp.route("/api/tasks", methods=["PUT"])
def ApiSaveTasks():
    tasks = JsonBody().get("tasks", [])
    if not isinstance(tasks, list):
        abort(400)

    error = SaveTasks(tasks)
    if error is not None:
        return ErrorResponse(error[0], index=error[1])
    return jsonify({"tasks": LoadTasks()})

@uiApp.route("/api/tasks/<url>", methods=["DELETE"])
def ApiDeleteTask(url):
    if not DeleteTaskFiles(url):
        abort(400)
    return jsonify({"ok": True})

@uiApp.route("/api/run/<url>", methods=["POST"])
def ApiRunTask(url):
    return jsonify({"message": StartTask(url)})

@uiApp.route("/api/log")
def ApiLog():
    return jsonify({"lines": ReadLogLines()})

@uiApp.route("/api/settings", methods=["PUT"])
def ApiSaveSettings():
    raw = JsonBody()

    port = ParsePort(raw.get("PORT", ""))
    if port is None:
        return ErrorResponse("PORT: 1-65535")

    flag = lambda key: "True" if str(raw.get(key, "False")) == "True" else "False"
    text = lambda key: str(raw.get(key, "")).strip()

    newSettings = {
        "PORT": port,
        "showNotifications": flag("showNotifications"),
        "closeToTrayOnStart": flag("closeToTrayOnStart"),
        "language": text("language") if text("language") in languagesList else CurrentLanguage(),
        "AllowedTG_IDs": text("AllowedTG_IDs"),
        "TG_TOKEN": text("TG_TOKEN"),
        "CheckWorkURL": text("CheckWorkURL"),
        "AdditionalURL": text("AdditionalURL"),
        "AutoStart": flag("AutoStart"),
        "NotifyOnStart": flag("NotifyOnStart"),
    }

    SaveSettings(newSettings)

    if newSettings["AutoStart"] == "True":
        LaunchWithoutConsole(["cmd", "/c", "LoadOnStartup.vbs"])
    else:
        LaunchWithoutConsole(["cmd", "/c", "NotLoadOnStartup.bat"])

    threading.Timer(RESPONSE_DELAY, RestartProgram).start()
    return jsonify({"ok": True})

@uiApp.route("/api/quit", methods=["POST"])
def ApiQuit():
    threading.Timer(RESPONSE_DELAY, QuitProgram).start()
    return jsonify({"ok": True})

def StartUiServer():
    global uiServerPort

    server = make_server("127.0.0.1", 0, uiApp, threaded=True)
    uiServerPort = server.server_port

    threading.Thread(target=server.serve_forever, name="UiServer", daemon=True).start()
    AddShutdownHandler(CloseWindow)
#endregion
