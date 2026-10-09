# HTTP-сервер для запуска задач по ссылке (локальная сеть / туннель) и фоновые проверки:
# дополнительный URL и перезапуск туннеля через RestartTunnel.vbs
import os
import threading
from time import sleep

import requests
from flask import Flask
from werkzeug.serving import make_server

from catpilot_config import Setting, settings
from catpilot_localization import Localize
from catpilot_log import LogToFile
from catpilot_notify import Notify
from catpilot_tasks import RunVbs, StartTask

CHECK_ROUTES = ("Call", "C")
IGNORED_ROUTES = ("favicon.ico", "robots.txt")

RESTART_TUNNEL_SCRIPT = "RestartTunnel.vbs"
REQUEST_TIMEOUT = 4
CHECK_INTERVAL = 60
AFTER_RESTART_INTERVAL = 10

#region Flask
app = Flask(__name__)

@app.route("/<page>")
def FlaskMain(page):
    if page in IGNORED_ROUTES:
        return "", 200

    if page in CHECK_ROUTES:
        return "Ok", 200

    return StartTask(page), 200

def RunServer():
    port = settings["PORT"]

    try:
        server = make_server("0.0.0.0", port, app, threaded=True)
    except Exception as e:
        # Чаще всего порт занят другой (например, не до конца закрытой) копией
        LogToFile("Flask server error (port " + str(port) + ") | " + str(e))
        Notify("Flask server error (port " + str(port) + "): " + str(e))
        return

    server.serve_forever()
#endregion

#region Watchdog
def IsTunnelCheckEnabled():
    return Setting("CheckWorkURL") != "" and os.path.exists(RESTART_TUNNEL_SCRIPT)

def RestartTunnel(reason):
    LogToFile("RestartTunnel, because " + reason)
    RunVbs(RESTART_TUNNEL_SCRIPT)

def PingAdditionalUrl():
    try:
        response = requests.get(Setting("AdditionalURL"), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        LogToFile(Localize("AdditionalURLResponse") + " | " + str(response) + " | " + response.text)
    except Exception as e:
        LogToFile("Additional URL error: " + str(e))

def CheckTunnel():
    """Проверяет, что программа доступна снаружи (CheckWorkURL отвечает "Ok"),
    иначе перезапускает туннель. Возвращает паузу до следующей проверки"""
    try:
        response = requests.get(Setting("CheckWorkURL"), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        if "Ok" in response.text:
            return CHECK_INTERVAL
        reason = "response was: " + response.text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        reason = "connection error"
    except requests.exceptions.HTTPError:
        reason = "HTTP Error"
    except Exception as e:
        reason = "exception: " + str(e)

    RestartTunnel(reason)
    return AFTER_RESTART_INTERVAL

def WatchdogLoop():
    if Setting("AdditionalURL") == "" and Setting("CheckWorkURL") == "":
        return

    while True:
        if Setting("AdditionalURL") != "":
            PingAdditionalUrl()

        delay = CHECK_INTERVAL
        if IsTunnelCheckEnabled():
            delay = CheckTunnel()

        sleep(delay)

def StartTunnelOnLaunch():
    if IsTunnelCheckEnabled():
        RunVbs(RESTART_TUNNEL_SCRIPT)
#endregion

def StartServers():
    threading.Thread(target=RunServer, name="Flask", daemon=True).start()
    threading.Thread(target=WatchdogLoop, name="Watchdog", daemon=True).start()
