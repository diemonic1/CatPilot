# Окно CatPilot: отдельный процесс (CatPilot.exe --gui), который запускает основная копия
# по «Показать». Интерфейс — веб-страница с локального сервера основной копии в WebView2.
# После закрытия окна процесс завершается, и в трее не остаётся ничего от интерфейса
import ctypes
import os
import sys
import traceback
from contextlib import suppress

import webview

from catpilot_config import ICON, PROGRAM_NAME
from catpilot_log import LogToFile

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6

class Api:
    """Методы, доступные странице как window.pywebview.api.*
    Поля начинаются с _, иначе pywebview полезет обходить их (и окно) как часть API"""

    def __init__(self):
        self._window = None
        self._dirty = False
        self._closeQuestion = "Close without saving?"

    def setDirty(self, dirty, closeQuestion):
        self._dirty = bool(dirty)
        self._closeQuestion = str(closeQuestion)

    def close(self):
        self._dirty = False
        self._window.destroy()

def WindowHandle(window):
    with suppress(Exception):
        return int(window.native.Handle.ToInt64())
    return None

def OnShown(window):
    # Тёмный заголовок окна Windows 11 под тёмную тему страницы
    hwnd = WindowHandle(window)
    if hwnd:
        with suppress(Exception):
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(ctypes.c_void_p(hwnd), DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))

def OnClosing(window, api):
    if not api._dirty:
        return True

    answer = ctypes.windll.user32.MessageBoxW(WindowHandle(window), api._closeQuestion, PROGRAM_NAME, MB_YESNO | MB_ICONWARNING)
    return answer == IDYES

def RunGui():
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    try:
        port = os.environ["CATPILOT_UI_PORT"]
        token = os.environ["CATPILOT_UI_TOKEN"]

        api = Api()
        window = webview.create_window(
            PROGRAM_NAME,
            "http://127.0.0.1:" + port + "/?token=" + token,
            js_api=api,
            width=1400,
            height=860,
            min_size=(900, 560),
            background_color="#1e1e1e",
            text_select=True,
        )
        api._window = window

        window.events.shown += lambda: OnShown(window)
        window.events.closing += lambda: OnClosing(window, api)

        webview.start(gui="edgechromium",
                      icon=ICON if os.path.isfile(ICON) else None,
                      private_mode=False,
                      storage_path=os.path.join(os.getenv("LOCALAPPDATA", os.getcwd()), PROGRAM_NAME, "WebView2"))
    except Exception:
        LogToFile("ERROR (gui) | " + traceback.format_exc().strip())
