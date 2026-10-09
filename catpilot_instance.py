# Единственная копия программы, выход и перезапуск
import ctypes
import os
import subprocess
import sys
from contextlib import suppress
from ctypes import wintypes

from catpilot_config import APP_DIR, PROGRAM_NAME
from catpilot_log import LogToFile

MUTEX_NAME = "CatPilot_SingleInstanceMutex"
SHOW_EVENT_NAME = "CatPilot_ShowWindowEvent"

ERROR_ALREADY_EXISTS = 183
EVENT_MODIFY_STATE = 0x0002
INFINITE = 0xFFFFFFFF

GUI_ARG = "--gui"
SHOW_ARG = "--show"
RESTART_ARG = "--restart"

# use_last_error: ctypes.windll.kernel32.GetLastError() может вернуть код от чужого вызова
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateEventW.restype = wintypes.HANDLE
kernel32.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.OpenEventW.restype = wintypes.HANDLE
kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.SetEvent.argtypes = [wintypes.HANDLE]
kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD

singleInstanceMutex = None
shutdownHandlers = []
shuttingDown = False

#region Single instance
def AlreadyRunning():
    global singleInstanceMutex

    try:
        mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.get_last_error() != ERROR_ALREADY_EXISTS:
            singleInstanceMutex = mutex
            return False

        # Свой хэндл на чужой мьютекс не держим: иначе он переживёт ту копию,
        # и ожидание при перезапуске никогда не закончится
        if mutex:
            kernel32.CloseHandle(mutex)
        return True
    except Exception as e:
        LogToFile("Single instance check error: " + str(e))
        return False

def ReleaseSingleInstanceMutex():
    global singleInstanceMutex

    if singleInstanceMutex:
        with suppress(Exception):
            kernel32.ReleaseMutex(singleInstanceMutex)
            kernel32.CloseHandle(singleInstanceMutex)
        singleInstanceMutex = None

def WaitForShowRequests(onShow):
    """Повторный запуск CatPilot.exe не плодит копию, а через это событие просит открыть окно"""
    event = kernel32.CreateEventW(None, False, False, SHOW_EVENT_NAME)
    if not event:
        return

    while True:
        kernel32.WaitForSingleObject(event, INFINITE)
        onShow()

def SignalRunningInstance():
    event = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, SHOW_EVENT_NAME)
    if event:
        kernel32.SetEvent(event)
        kernel32.CloseHandle(event)
    return bool(event)
#endregion

#region Exit
def AddShutdownHandler(handler):
    """Модули регистрируют здесь свою остановку (окно, трей, бот), чтобы выход
    и перезапуск не зависели от них напрямую"""
    shutdownHandlers.append(handler)

def RunShutdownHandlers():
    global shuttingDown

    if shuttingDown:
        return
    shuttingDown = True

    for handler in shutdownHandlers:
        with suppress(Exception):
            handler()

def ExitProgram(code=0):
    """Завершает процесс, не дожидаясь daemon-потоков (Flask, бот, туннель):
    их остановка на этапе finalization роняет процесс и оставляет занятым порт"""
    RunShutdownHandlers()
    os._exit(code)

def QuitProgram():
    LogToFile("Closing " + PROGRAM_NAME)
    ExitProgram()

def SelfCommand(*args):
    if getattr(sys, "frozen", False):
        return [sys.executable] + list(args)
    return [sys.executable, os.path.join(APP_DIR, "CatPilot.py")] + list(args)

def RestartProgram():
    LogToFile("Restarting " + PROGRAM_NAME)
    # Бот останавливается до запуска новой копии: два polling одного токена конфликтуют
    RunShutdownHandlers()
    ReleaseSingleInstanceMutex()
    subprocess.Popen(SelfCommand(RESTART_ARG, SHOW_ARG), creationflags=subprocess.CREATE_NO_WINDOW)
    os._exit(0)
#endregion
