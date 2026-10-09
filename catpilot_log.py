# log.txt: новые строки сверху, хранится не больше LOG_MAX_LINES последних записей.
# Модуль лёгкий — его использует и процесс окна (catpilot_gui.py)
import sys
import threading
import traceback
from contextlib import suppress
from datetime import datetime

from catpilot_config import AppPath

LOG_FILE = AppPath("log.txt")
LOG_MAX_LINES = 50

logLock = threading.Lock()

def LogToFile(message):
    message = str(message)
    if message == "":
        return

    # Многострочные сообщения (трейсбеки) складываем в одну строку:
    # логгер и окно лога работают построчно
    line = str(datetime.now()) + " | " + message.replace("\r", "").replace("\n", " | ")

    with logLock, suppress(OSError):
        lines = ReadLogLines()
        with open(LOG_FILE, "w", encoding="utf-8") as file:
            file.write("\n".join([line] + lines[:LOG_MAX_LINES - 1]) + "\n")

def ReadLogLines():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def LogException(source, excType, excValue, excTraceback):
    text = "".join(traceback.format_exception(excType, excValue, excTraceback)).strip()
    LogToFile("ERROR (" + str(source) + ") | " + text)

def InstallExceptionHooks():
    """В сборке без консоли sys.stderr подменён на заглушку, поэтому
    единственный способ увидеть падение — писать его в log.txt"""
    def logUnhandledException(excType, excValue, excTraceback):
        LogException("main", excType, excValue, excTraceback)

    def logThreadException(args):
        if args.exc_type is SystemExit:
            return
        LogException("thread " + str(args.thread.name if args.thread else "?"),
                     args.exc_type, args.exc_value, args.exc_traceback)

    sys.excepthook = logUnhandledException
    threading.excepthook = logThreadException
