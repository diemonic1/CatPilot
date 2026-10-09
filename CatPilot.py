import sys

# Окно — отдельный процесс (CatPilot.exe --gui), который запускает основная копия.
# Ветка стоит до остальных импортов: окну не нужны ни бот, ни pyautogui, ни Flask
if __name__ == "__main__" and "--gui" in sys.argv:
    from catpilot_gui import RunGui
    RunGui()
    sys.exit(0)

import os

# В сборке --windowed PyInstaller оставляет sys.stdout/sys.stderr = None,
# а print/логгеры библиотек ожидают файл
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import threading
from time import sleep

import catpilot_config
from catpilot_config import IsOn, PROGRAM_NAME, settings
from catpilot_log import InstallExceptionHooks, LogException, LogToFile

catpilot_config.UseAppDirectory()
InstallExceptionHooks()
settingsError = catpilot_config.LoadSettings()

from catpilot_bot import StartBot
from catpilot_instance import (AlreadyRunning, ExitProgram, RESTART_ARG, SHOW_ARG,
                               SignalRunningInstance, WaitForShowRequests)
from catpilot_localization import LoadLocalizations, Localize
from catpilot_notify import Notify
from catpilot_server import StartServers, StartTunnelOnLaunch
from catpilot_tasks import ReloadTasks
from catpilot_tray import RunTray
from catpilot_window import ShowWindow, StartUiServer

RESTART_WAIT_ATTEMPTS = 50
RESTART_WAIT_STEP = 0.2

def WaitForOtherInstance():
    """Возвращает True, если уже работает другая копия. При перезапуске после
    сохранения настроек сначала ждёт, пока старая копия закроется"""
    alreadyRunning = AlreadyRunning()

    if alreadyRunning and RESTART_ARG in sys.argv:
        for attempt in range(RESTART_WAIT_ATTEMPTS):
            sleep(RESTART_WAIT_STEP)
            alreadyRunning = AlreadyRunning()
            if not alreadyRunning:
                break

    return alreadyRunning

def Main():
    if settingsError:
        LogToFile(settingsError)

    if WaitForOtherInstance():
        # Уже запущенная копия сама откроет своё окно
        if SignalRunningInstance():
            LogToFile(PROGRAM_NAME + " is already running, opened its window, second copy closed")
        else:
            LogToFile(PROGRAM_NAME + " is already running, second copy closed")
            Notify(PROGRAM_NAME + " is already running", wait=True)
        ExitProgram()

    LoadLocalizations()
    ReloadTasks()

    StartServers()
    StartBot()
    StartTunnelOnLaunch()

    if IsOn("NotifyOnStart"):
        Notify(Localize("NotifyOnStartMessage"))

    try:
        StartUiServer()
        threading.Thread(target=WaitForShowRequests, args=(ShowWindow,), name="ShowRequests", daemon=True).start()

        if not IsOn("closeToTrayOnStart") or SHOW_ARG in sys.argv:
            ShowWindow()

        LogToFile(Localize("runOn") + " " + str(settings["PORT"]))

        RunTray(ShowWindow)
    except Exception:
        LogException("main", *sys.exc_info())
        Notify(PROGRAM_NAME + " crashed, see log.txt", wait=True)
        ExitProgram(1)

    ExitProgram()

if __name__ == "__main__":
    Main()
