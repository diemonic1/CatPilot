import sys

# Окно — отдельный процесс (CatPilot.exe --gui), который запускает основная копия.
# Ветка стоит до остальных импортов: окну не нужны ни бот, ни pyautogui, ни Flask
if __name__ == "__main__" and "--gui" in sys.argv:
    from catpilot_gui import RunGui
    RunGui()
    sys.exit(0)

from time import sleep
from contextlib import suppress

import ctypes
import re
import secrets
import traceback
import unicodedata
import winreg
import pyautogui
import time
import telebot
from telebot import types
from requests import get
import requests.exceptions
import threading
from flask import Flask, Response, abort, jsonify, request
from werkzeug.serving import make_server
from datetime import datetime
from pystray import MenuItem as item, Menu
import pystray
from PIL import Image, ImageChops, ImageDraw, ImageFont
import subprocess
import os
from win11toast import toast
import asyncio
import json

# В сборке --windowed PyInstaller оставляет sys.stdout/sys.stderr = None,
# а print/логгеры библиотек ожидают файл
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

PROGRAM_NAME = "CatPilot"
PROGRAM_VERSION = "2.0.0"
ICON_RAW = "CatPilot.ico"
ICON = os.getcwd() + "\\" + ICON_RAW

COMMANDS_TO_START_BOT = "/start /help /commands /начать /помощь /команды"

STAR_ICON = "*"
SPACE_SYMBOL = "%20"

MUTEX_NAME = "CatPilot_SingleInstanceMutex"
ERROR_ALREADY_EXISTS = 183

WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016

SHOW_EVENT_NAME = "CatPilot_ShowWindowEvent"
EVENT_MODIFY_STATE = 0x0002
INFINITE = 0xFFFFFFFF
ASFW_ANY = -1
SW_RESTORE = 9

GUI_ARG = "--gui"
SHOW_ARG = "--show"
RESTART_ARG = "--restart"
GUI_PORT_ENV = "CATPILOT_UI_PORT"
GUI_TOKEN_ENV = "CATPILOT_UI_TOKEN"

singleInstanceMutex = None

#region Settings

PORT = ""
showNotifications = ""
closeToTrayOnStart = ""
LANGUAGE = ""
AllowedTG_IDs = ""
TG_TOKEN = ""
CheckWorkURL = ""
AdditionalURL = ""
AutoStart = ""
NotifyOnStart = ""

find_settings = False

for filename in os.listdir(os.getcwd()):
    f = os.path.join(os.getcwd(), filename)
    if os.path.isfile(f) and "Settings.json" in filename:
        find_settings = True

if find_settings == False:
    file = open('Settings.json', 'a', encoding='utf-8')
    file.write('{ "PORT": 5000, "showNotifications": "True", "closeToTrayOnStart": "False", "language": "English", "AllowedTG_IDs": "", "TG_TOKEN": "", "CheckWorkURL": "", "AdditionalURL": "", "NotifyOnStart": "False" }')
    file.close()

def UpdateSettings():
    f = open('Settings.json', encoding='utf-8')
    data = json.load(f)
    f.close()
    global PORT
    global showNotifications
    global closeToTrayOnStart
    global LANGUAGE
    global AllowedTG_IDs
    global TG_TOKEN
    global CheckWorkURL
    global AdditionalURL
    global AutoStart
    global NotifyOnStart
    PORT = data['PORT']
    showNotifications = data['showNotifications']
    closeToTrayOnStart = data['closeToTrayOnStart']
    LANGUAGE = data['language']
    AllowedTG_IDs = data['AllowedTG_IDs']
    TG_TOKEN = data['TG_TOKEN']
    CheckWorkURL = data['CheckWorkURL']
    AdditionalURL = data['AdditionalURL']
    try:
        AutoStart = data['AutoStart']
    except Exception:
        AutoStart = "False"
    try:
        NotifyOnStart = data['NotifyOnStart']
    except Exception:
        NotifyOnStart = "False"

UpdateSettings()

#endregion

# region Localization
localizationWasSet = False
languagesList = ["English"]
localizationDict = {}

def Localize(key):
    global localizationWasSet
    global languagesList
    global localizationDict
    global LANGUAGE

    if not localizationWasSet:
        languagesList = []

        for filename in os.listdir(os.getcwd() + "\\Localization"):
            fPath = os.path.join(os.getcwd() + "\\Localization", filename)
            file = open(fPath, "r", encoding='utf-8')
            languageName = filename[:-5]
            localization = json.load(file)
            file.close()
            languagesList.append(languageName)
            localizationDict[languageName] = localization
        localizationWasSet = True

    try:
        return localizationDict[LANGUAGE][key]
    except Exception:
        Notify('Not find language "' + LANGUAGE + '" or key "' + key + '" in localization.json, set English language')
        LANGUAGE = "English"
        return localizationDict[LANGUAGE][key]

# endregion

#region Logger
def logToFile(message):
    if str(message) == "":
        return

    # Многострочные сообщения (трейсбеки) складываем в одну строку:
    # логгер и окно лога работают построчно
    message = str(message).replace("\r", "").replace("\n", " | ")

    open('log.txt', 'a', encoding='utf-8').close()

    file = open("log.txt", "r", encoding='utf-8')
    linesCount = len(file.readlines())
    file.close()

    if linesCount > 50:
        open('log.txt', 'w', encoding='utf-8').close()

    file = open('log.txt', 'r+', encoding='utf-8')
    content = file.read()  # Чтение
    file.seek(0, 0)  # Переход в начало файла
    file.write(str(datetime.now()) + " | " + str(message) + "\n")
    file.write(content)
    file.close()

def logException(source, excType, excValue, excTraceback):
    text = "".join(traceback.format_exception(excType, excValue, excTraceback)).strip()
    logToFile("ERROR (" + str(source) + ") | " + text)

def logUnhandledException(excType, excValue, excTraceback):
    logException("main", excType, excValue, excTraceback)

def logThreadException(args):
    if args.exc_type is SystemExit:
        return
    logException("thread " + str(args.thread.name if args.thread else "?"),
                 args.exc_type, args.exc_value, args.exc_traceback)

# В сборке без консоли sys.stderr подменён на заглушку (PyInstaller NullWriter),
# поэтому единственный способ увидеть падение — писать его в log.txt
sys.excepthook = logUnhandledException
threading.excepthook = logThreadException
#endregion

#region Notify
async def NotifyAsync(message):
    toast(message, PROGRAM_NAME, icon=ICON)

def Notify(message):
    asyncio.run(NotifyAsync(message))
#endregion

#region Exit
def AlreadyRunning():
    global singleInstanceMutex

    try:
        kernel32 = ctypes.windll.kernel32
        singleInstanceMutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if kernel32.GetLastError() != ERROR_ALREADY_EXISTS:
            return False

        # Свой хэндл на чужой мьютекс не держим: иначе он переживёт ту копию,
        # и ожидание при перезапуске никогда не закончится
        kernel32.CloseHandle(singleInstanceMutex)
        singleInstanceMutex = None
        return True
    except Exception as e:
        logToFile("Single instance check error: " + str(e))
        return False

def ReleaseSingleInstanceMutex():
    global singleInstanceMutex

    if singleInstanceMutex:
        with suppress(Exception):
            ctypes.windll.kernel32.ReleaseMutex(singleInstanceMutex)
            ctypes.windll.kernel32.CloseHandle(singleInstanceMutex)
        singleInstanceMutex = None

def StopBackgroundThreads():
    if TG_TOKEN != "":
        with suppress(Exception):
            bot.stop_polling()

def ExitProgram(code=0):
    """Завершает процесс, не дожидаясь daemon-потоков (Flask, бот, туннель):
    их остановка на этапе finalization роняет процесс и оставляет занятым порт"""
    StopBackgroundThreads()
    os._exit(code)
#endregion

#region PressButtons
buttons = ['None', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
'8', '9', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`',
'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
'browserback', 'browserfavorites', 'browserforward', 'browserhome',
'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
'command', 'option', 'optionleft', 'optionright']

def PressButtons(b1):
    pyautogui.keyDown(b1)
    pyautogui.keyUp(b1)

def PressButtons2(b1, b2):
    pyautogui.keyDown(b1)
    pyautogui.keyDown(b2)
    pyautogui.keyUp(b1)
    pyautogui.keyUp(b2)

def PressButtons3(b1, b2, b3):
    pyautogui.keyDown(b1)
    pyautogui.keyDown(b2)
    pyautogui.keyDown(b3)
    pyautogui.keyUp(b1)
    pyautogui.keyUp(b2)
    pyautogui.keyUp(b3)
#endregion

#region Tasker
def launchWithoutConsole(command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(command, startupinfo=startupinfo).wait()

def StartTask(taskURL):
    result = ""

    try:
        osResult = launchWithoutConsole(["cmd", "/c", "Tasks\\" + taskURL + ".vbs"])

        if (osResult == 0):
            file = open(os.getcwd() + "\\Tasks\\" + taskURL + ".settings", "r", encoding='utf-8')
            contentFromFile = json.loads(str(file.read()))
            file.close()

            result = Localize("success")

            if showNotifications == "True" and contentFromFile["notify"] == "True":
                Notify(contentFromFile["name"])

            buttonsFromFile = []

            if contentFromFile["button1"] != "None":
                buttonsFromFile.append(contentFromFile["button1"])
            if contentFromFile["button2"] != "None":
                buttonsFromFile.append(contentFromFile["button2"])
            if contentFromFile["button3"] != "None":
                buttonsFromFile.append(contentFromFile["button3"])

            if len(buttonsFromFile) == 1:
                PressButtons(buttonsFromFile[0])
            elif len(buttonsFromFile) == 2:
                PressButtons2(buttonsFromFile[0], buttonsFromFile[1])
            elif len(buttonsFromFile) == 3:
                PressButtons3(buttonsFromFile[0], buttonsFromFile[1], buttonsFromFile[2])
        else:
            result = taskURL + " | " + Localize("fail")
            Notify(result)

    except Exception as e:
        result = str(e)

    message = taskURL.replace(SPACE_SYMBOL, " ") + " | " + result
    logToFile(message)

    return message
#endregion

#region Tasks
# Задача на диске — пара файлов Tasks\<url>.vbs (скрипт) и Tasks\<url>.settings (json)
TASKS_DIR = "Tasks"
TASK_FLAGS = ("notify", "tgBOT", "trayCommand")

possibleTasksForBot = {}
tasksLock = threading.Lock()

def TasksFolder():
    folder = os.path.join(os.getcwd(), TASKS_DIR)
    os.makedirs(folder, exist_ok=True)
    return folder

def LoadTasks():
    folder = TasksFolder()
    tasks = []

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".vbs"):
            continue

        url = filename[:-4]

        with open(os.path.join(folder, filename), "r", encoding='utf-8') as file:
            script = file.read().rstrip()

        settingsFromFile = {}
        with suppress(Exception):
            with open(os.path.join(folder, url + ".settings"), "r", encoding='utf-8') as file:
                settingsFromFile = json.load(file)

        task = {"url": url, "script": script, "name": str(settingsFromFile.get("name", url))}

        for key in ("button1", "button2", "button3"):
            task[key] = str(settingsFromFile.get(key, "None"))

        for key in TASK_FLAGS:
            task[key] = str(settingsFromFile.get(key, "True"))

        tasks.append(task)

    return tasks

def ValidateTasks(tasks):
    """Возвращает (текст ошибки, индекс задачи) или None"""
    for i, task in enumerate(tasks):
        if task["url"] == "" or task["name"] == "" or task["script"].strip() == "":
            return Localize("emptyError"), i

        if not re.match("^[a-zA-Z0-9]+$", task["url"]):
            return Localize("notAllowedURLError"), i

    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            for key in ("url", "name"):
                if tasks[i][key] == tasks[j][key]:
                    return Localize("copyError") + " | " + tasks[i][key] + " | №" + str(i + 1) + ", №" + str(j + 1), j

    return None

def NormalizeTask(raw):
    task = {"url": str(raw.get("url", "")).strip(),
            "name": str(raw.get("name", "")).strip(),
            "script": str(raw.get("script", "")).replace("\r\n", "\n")}

    for key in ("button1", "button2", "button3"):
        value = str(raw.get(key, "None"))
        task[key] = value if value in buttons else "None"

    for key in TASK_FLAGS:
        task[key] = "True" if str(raw.get(key, "True")) == "True" else "False"

    return task

def SaveTasks(rawTasks):
    tasks = [NormalizeTask(raw) for raw in rawTasks]

    error = ValidateTasks(tasks)
    if error is not None:
        return error

    with tasksLock:
        folder = TasksFolder()

        for filename in os.listdir(folder):
            if filename.endswith(".vbs") or filename.endswith(".settings"):
                os.remove(os.path.join(folder, filename))

        for task in tasks:
            with open(os.path.join(folder, task["url"] + ".vbs"), "w", encoding='utf-8') as file:
                file.write(task["script"].rstrip() + "\n")

            settingsForFile = {key: task[key] for key in ("button1", "button2", "button3", "name") + TASK_FLAGS}
            with open(os.path.join(folder, task["url"] + ".settings"), "w", encoding='utf-8') as file:
                json.dump(settingsForFile, file, ensure_ascii=False)

    ReloadTasks()
    return None

def DeleteTaskFiles(url):
    with tasksLock:
        for extension in (".vbs", ".settings"):
            path = os.path.join(TasksFolder(), url + extension)
            if os.path.isfile(path):
                os.remove(path)

    ReloadTasks()

def ReloadTasks():
    """Перечитывает задачи с диска и обновляет всё, что от них зависит: список бота и меню трея"""
    tasks = LoadTasks()

    possibleTasksForBot.clear()
    for task in tasks:
        possibleTasksForBot[task["name"]] = {"urlEntry": task["url"], "tgBOT_check_var": task["tgBOT"]}

    if trayIcon is not None:
        with suppress(Exception):
            trayIcon.menu = BuildTrayMenu(tasks)

    return tasks
#endregion

#region Tray icons
# Меню трея — классическое Win32-меню, его текст рисует GDI: цветные эмодзи он не умеет,
# а символов, которых нет в Segoe UI и его запасных шрифтах (🥽, ᯅ, ⛶), не показывает вовсе.
# Поэтому значок из названия задачи рисуем картинкой и ставим слева от пункта
MIIM_BITMAP = 0x00000080
SM_CXSMICON = 49

# Первый шрифт, в котором есть символ, и рисует значок. Segoe UI Emoji — цветной,
# остальные монохромные (рисуются цветом текста меню). SansSerifCollection есть только в Windows 11
ICON_FONTS = ["seguiemj.ttf", "seguisym.ttf", "SansSerifCollection.ttf", "seguihis.ttf"]
ICON_RENDER_SIZE = 96
ICON_JOINERS = "\u200d\ufe0e\ufe0f\u20e3"  # ZWJ, селекторы вида, keycap

trayBitmaps = {}
iconFonts = None

def IsIconChar(ch):
    if ch in ICON_JOINERS:
        return True
    if ch.isascii():
        return False

    category = unicodedata.category(ch)
    if category.startswith("S"):
        return True
    if category.startswith("L"):
        # Буква редкой письменности как значок (ᯅ), но не обычный текст
        return not unicodedata.name(ch, "").startswith(("LATIN", "CYRILLIC", "GREEK"))
    return False

def SplitTrayIcon(name):
    """Возвращает (значок или None, текст без значка). Значок — первая подряд идущая
    последовательность символов-значков в названии; все её вхождения убираются из текста"""
    match = None
    for found in re.finditer("[^\\s]+", name):
        run = ""
        for ch in found.group():
            if IsIconChar(ch):
                run += ch
            elif run:
                break
        letters = [ch for ch in run if unicodedata.category(ch).startswith("L")]
        # Несколько букв подряд — уже слово, а не значок
        if run.strip(ICON_JOINERS) and len(letters) <= 1 and (not letters or len(run.strip(ICON_JOINERS)) == 1):
            match = run
            break

    if match is None:
        return None, name

    text = " ".join(name.replace(match, " ").split())
    return match, text if text else name

def LoadIconFonts():
    fonts = []
    fontsFolder = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")

    for fileName in ICON_FONTS:
        with suppress(Exception):
            font = ImageFont.truetype(os.path.join(fontsFolder, fileName), ICON_RENDER_SIZE * 2 // 3)
            # Как выглядит отсутствующий символ (.notdef) — чтобы отличать «нет символа» от значка
            fonts.append((font, RenderIconGlyph(font, "\U000F0000", (0, 0, 0, 255)).tobytes()))

    return fonts

def RenderIconGlyph(font, icon, color):
    image = Image.new("RGBA", (ICON_RENDER_SIZE * 2, ICON_RENDER_SIZE * 2), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((ICON_RENDER_SIZE // 2, ICON_RENDER_SIZE // 2), icon, font=font, fill=color, embedded_color=True)
    return image

def MenuTextColor():
    # Меню трея следует теме приложений Windows (см. SetPreferredAppMode в RunTray)
    with suppress(Exception):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            if winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0:
                return (240, 240, 240, 255)
    return (0, 0, 0, 255)

def RenderIconImage(icon, size):
    global iconFonts

    if iconFonts is None:
        iconFonts = LoadIconFonts()

    for font, missingGlyph in iconFonts:
        image = RenderIconGlyph(font, icon, MenuTextColor())
        box = image.getbbox()

        if box is None or RenderIconGlyph(font, icon, (0, 0, 0, 255)).tobytes() == missingGlyph:
            continue

        # Обрезаем по содержимому и вписываем в квадрат: у символов разная ширина и отступы
        image = image.crop(box)
        scale = size / max(image.size)
        image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)

        square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        square.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
        return square

    return None

def CreateMenuBitmap(image):
    """32-битный DIB с premultiplied alpha — так Windows рисует картинку пункта меню с прозрачностью"""
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                    ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

    header = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), image.width, -image.height, 1, 32, 0, 0, 0, 0, 0, 0)

    red, green, blue, alpha = image.split()
    pixels = Image.merge("RGBA", (ImageChops.multiply(blue, alpha), ImageChops.multiply(green, alpha),
                                  ImageChops.multiply(red, alpha), alpha)).tobytes()

    gdi32 = ctypes.windll.gdi32
    gdi32.CreateDIBSection.restype = ctypes.c_void_p
    gdi32.CreateDIBSection.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_uint32]

    bits = ctypes.c_void_p()
    bitmap = gdi32.CreateDIBSection(None, ctypes.byref(header), 0, ctypes.byref(bits), None, 0)
    if not bitmap or not bits.value:
        return None

    ctypes.memmove(bits, pixels, len(pixels))
    return bitmap

def TrayItemTextAndBitmap(name):
    """Текст пункта меню и картинка значка из названия задачи. Если значка нет или его
    нечем нарисовать — пункт остаётся как есть: исходное название без картинки"""
    icon, text = SplitTrayIcon(name)
    if icon is None:
        return name, None

    if icon not in trayBitmaps:
        bitmap = None
        with suppress(Exception):
            image = RenderIconImage(icon, ctypes.windll.user32.GetSystemMetrics(SM_CXSMICON) or 16)
            if image is not None:
                bitmap = CreateMenuBitmap(image)
        # Картинки живут до конца работы программы: меню пересоздаётся, а значков немного
        trayBitmaps[icon] = bitmap

    if trayBitmaps[icon] is None:
        return name, None

    return text, trayBitmaps[icon]
#endregion

#region Tray
# Пока программа в трее, кроме pystray (чистый Win32) никакого интерфейса нет:
# окно — отдельный процесс, который создаётся только по «Показать»
trayIcon = None

class TrayIcon(pystray.Icon):
    """pystray.Icon, у пунктов меню которого может быть картинка слева (MenuItem.iconBitmap)"""

    def _create_menu_item(self, descriptor, callbacks):
        menuItem = super()._create_menu_item(descriptor, callbacks)

        bitmap = getattr(descriptor, "iconBitmap", None)
        if bitmap:
            menuItem.fMask |= MIIM_BITMAP
            menuItem.hbmpItem = bitmap

        return menuItem

def StartTaskInBackground(url):
    # Задача ждёт завершения vbs, а меню трея не должно подвисать
    threading.Thread(target=StartTask, args=(url,), daemon=True).start()

def BuildTrayMenu(tasks):
    menuItems = []

    for task in tasks:
        if task["trayCommand"] == "True":
            text, bitmap = TrayItemTextAndBitmap(task["name"])
            menuItem = item(text, (lambda url: lambda: StartTaskInBackground(url))(task["url"]))
            menuItem.iconBitmap = bitmap
            menuItems.append(menuItem)

    menuItems.append(Menu.SEPARATOR)
    menuItems.append(item(Localize("show"), lambda: ShowWindow(), default=True))
    menuItems.append(item(Localize("quit"), lambda: QuitProgram()))

    return Menu(*menuItems)

def OnEndSession(wparam, lparam):
    """Windows завершает сеанс. Окно pystray на необработанные сообщения
    отвечает 0, что для WM_QUERYENDSESSION означает запрет выключения,
    поэтому подтверждаем выход и закрываемся сами"""
    if wparam:
        logToFile("Windows session is ending, closing " + PROGRAM_NAME)
        CloseWindow()
        ExitProgram()
    return 0

def HideTray():
    if trayIcon is not None:
        # visible = False сразу удаляет иконку (NIM_DELETE), иначе после os._exit
        # в трее остаётся «призрак» до наведения мыши
        with suppress(Exception):
            trayIcon.visible = False

def RunTray():
    global trayIcon

    # Тёмное контекстное меню трея
    with suppress(Exception):
        ctypes.windll['uxtheme.dll'][135](1)

    icon = TrayIcon(PROGRAM_NAME, Image.open(ICON_RAW), PROGRAM_NAME, menu=BuildTrayMenu(LoadTasks()))
    icon._message_handlers[WM_QUERYENDSESSION] = lambda wparam, lparam: 1
    icon._message_handlers[WM_ENDSESSION] = OnEndSession

    trayIcon = icon
    icon.run()

def QuitProgram():
    logToFile("Closing " + PROGRAM_NAME)
    CloseWindow()
    HideTray()
    ExitProgram()

def SelfCommand(*args):
    if getattr(sys, "frozen", False):
        return [sys.executable] + list(args)
    return [sys.executable, os.path.abspath(__file__)] + list(args)

def RestartProgram():
    logToFile("Restarting " + PROGRAM_NAME)
    CloseWindow()
    HideTray()
    ReleaseSingleInstanceMutex()
    subprocess.Popen(SelfCommand(RESTART_ARG, SHOW_ARG), creationflags=subprocess.CREATE_NO_WINDOW)
    ExitProgram()
#endregion

#region Window process
guiProcess = None
guiLock = threading.Lock()
uiServerPort = 0
uiToken = secrets.token_urlsafe(24)

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

def ShowWindow():
    global guiProcess

    with guiLock:
        if guiProcess is not None and guiProcess.poll() is None:
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
        if guiProcess is not None and guiProcess.poll() is None:
            with suppress(Exception):
                guiProcess.terminate()

def WaitForShowRequests():
    """Повторный запуск CatPilot.exe не плодит копию, а через это событие просит открыть окно"""
    kernel32 = ctypes.windll.kernel32
    event = kernel32.CreateEventW(None, False, False, SHOW_EVENT_NAME)
    if not event:
        return

    while True:
        kernel32.WaitForSingleObject(event, INFINITE)
        ShowWindow()

def SignalRunningInstance():
    kernel32 = ctypes.windll.kernel32
    event = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, SHOW_EVENT_NAME)
    if event:
        kernel32.SetEvent(event)
        kernel32.CloseHandle(event)
    return bool(event)
#endregion

#region Window API
# Отдельный сервер только для окна: слушает 127.0.0.1 на случайном порту и требует токен.
# Основной Flask (0.0.0.0) запускает задачу на любой /<page>, поэтому смешивать их нельзя
uiApp = Flask("CatPilotUI")
monacoArchive = None

UI_MIME_TYPES = {".js": "application/javascript", ".css": "text/css", ".ttf": "font/ttf", ".html": "text/html"}

def UiResponse(content, mimetype, cache=False):
    response = Response(content, mimetype=mimetype)
    response.headers["Cache-Control"] = "max-age=86400" if cache else "no-store"
    return response

def ReadSettingsDict():
    with open('Settings.json', encoding='utf-8') as file:
        return json.load(file)

def UiStrings():
    Localize("show")  # подгружает localizationDict
    strings = dict(localizationDict.get("English", {}))
    strings.update(localizationDict.get(LANGUAGE, {}))
    return strings

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
    Localize("show")
    return jsonify({
        "program": PROGRAM_NAME,
        "version": PROGRAM_VERSION,
        "port": PORT,
        "strings": UiStrings(),
        "languages": languagesList,
        "buttons": buttons,
        "settings": ReadSettingsDict(),
        "tasks": LoadTasks(),
    })

@uiApp.route("/api/tasks", methods=["PUT"])
def ApiSaveTasks():
    error = SaveTasks(request.get_json(force=True).get("tasks", []))
    if error is not None:
        return jsonify({"error": error[0], "index": error[1]}), 400
    return jsonify({"tasks": LoadTasks()})

@uiApp.route("/api/tasks/<url>", methods=["DELETE"])
def ApiDeleteTask(url):
    DeleteTaskFiles(url)
    return jsonify({"ok": True})

@uiApp.route("/api/run/<url>", methods=["POST"])
def ApiRunTask(url):
    return jsonify({"message": StartTask(url)})

@uiApp.route("/api/log")
def ApiLog():
    open('log.txt', 'a', encoding='utf-8').close()
    with open("log.txt", "r", encoding='utf-8') as file:
        return jsonify({"lines": file.read().splitlines()})

@uiApp.route("/api/settings", methods=["PUT"])
def ApiSaveSettings():
    raw = request.get_json(force=True)

    try:
        port = int(str(raw.get("PORT", "")).strip())
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError:
        return jsonify({"error": "PORT: 1-65535"}), 400

    flag = lambda key: "True" if str(raw.get(key, "False")) == "True" else "False"
    text = lambda key: str(raw.get(key, "")).strip()

    settings = {
        "PORT": port,
        "showNotifications": flag("showNotifications"),
        "closeToTrayOnStart": flag("closeToTrayOnStart"),
        "language": text("language") if text("language") in languagesList else LANGUAGE,
        "AllowedTG_IDs": text("AllowedTG_IDs"),
        "TG_TOKEN": text("TG_TOKEN"),
        "CheckWorkURL": text("CheckWorkURL"),
        "AdditionalURL": text("AdditionalURL"),
        "AutoStart": flag("AutoStart"),
        "NotifyOnStart": flag("NotifyOnStart"),
    }

    with open('Settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file, ensure_ascii=False)

    if settings["AutoStart"] == "True":
        launchWithoutConsole(["cmd", "/c", "LoadOnStartup.vbs"])
    else:
        launchWithoutConsole(["cmd", "/c", "NotLoadOnStartup.bat"])

    # Перезапуск после ответа, чтобы окно успело его получить
    threading.Timer(0.3, RestartProgram).start()
    return jsonify({"ok": True})

@uiApp.route("/api/quit", methods=["POST"])
def ApiQuit():
    threading.Timer(0.3, QuitProgram).start()
    return jsonify({"ok": True})

def StartUiServer():
    global uiServerPort

    server = make_server("127.0.0.1", 0, uiApp, threaded=True)
    uiServerPort = server.server_port

    uiThread = threading.Thread(target=server.serve_forever, name="UiServer")
    uiThread.daemon = True
    uiThread.start()
#endregion

#region Flask
app = Flask(__name__)

@app.route('/<page>')
def FlaskMain(page):
    if str(page) == "favicon.ico" or str(page) == "robots.txt":
        return "",200

    if str(page) == "Call" or str(page) == "C":
        return "Ok", 200

    result = StartTask(str(page).replace(" ", SPACE_SYMBOL))
    return result, 200

def flask_main():
    try:
        app.run(host="0.0.0.0",port=PORT)
    except Exception as e:
        # Чаще всего порт занят другой (например, не до конца закрытой) копией
        logToFile("Flask server error (port " + str(PORT) + ") | " + str(e))
        with suppress(Exception):
            Notify("Flask server error (port " + str(PORT) + "): " + str(e))
#endregion

#region AppServerHandler

def AppServerHandler():
    global CheckWorkURL
    global AdditionalURL

    while True:
        if AdditionalURL == "" and CheckWorkURL == "":
            return

        try:
            if AdditionalURL != "":
                response = get(AdditionalURL, timeout=4)
                response.raise_for_status()
                logToFile(Localize("AdditionalURLResponse") + " | " + str(response) + " | " + str(response.text))
        except Exception as e:
            logToFile("Additional URL error: " + str(e))

        try:
            if CheckWorkURL != "" and os.path.exists("RestartTunnel.vbs"):
                response = get(CheckWorkURL, timeout=4)
                response.raise_for_status()
                try:
                    if not "Ok" in str(response.text):
                        logToFile("RestartTunnel, because response was: " + str(response.text))
                        launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
                        sleep(10)
                    else:
                        sleep(60)
                except Exception as e:
                    logToFile("RestartTunnel, because exception: " + str(e))
                    launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
                    sleep(10)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            logToFile("RestartTunnel, because connection error")
            launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
            sleep(10)
        except requests.exceptions.HTTPError:
            logToFile("RestartTunnel, because HTTP Error")
            launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
            sleep(10)
        except Exception as e:
            logToFile("RestartTunnel, because exception: " + str(e))
            launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
            sleep(10)

#endregion

#region Bot

if TG_TOKEN != "":
    bot = telebot.TeleBot(TG_TOKEN)

    def RunTaskFromTG(message, chatID):
        if message in possibleTasksForBot.keys():
            task = possibleTasksForBot[message]["urlEntry"]
            result = StartTask(task)
            bot.send_message(chatID, text=Localize("CarryOut"))
        else:
            for key, value in possibleTasksForBot.items():
                if value["urlEntry"] == message:
                    result = StartTask(message)
                    bot.send_message(chatID, text=Localize("CarryOut"))
                    return

            answer = message + " | " + Localize("fail")
            bot.send_message(chatID, text=answer)

    async def delete_message(chat_id, message_id, delay):
        time.sleep(delay)
        bot.delete_message(chat_id, message_id)

    @bot.callback_query_handler(func=lambda callback: True)
    def CallbackMessage(callback):
        message = callback.data
        RunTaskFromTG(message, callback.id)

    @bot.message_handler(func=lambda message: True)
    def get_text_messages(message):
        chat_id = message.chat.id
        meesage_id = message.id

        if not str(message.from_user.id) in AllowedTG_IDs:
            logToFile("TG BOT: " + Localize("NotAllowed"))
            bot.send_message(chat_id, text=Localize("NotAllowed"))
            return

        message = message.text

        if str(message).lower() in COMMANDS_TO_START_BOT:
            markup=types.InlineKeyboardMarkup()

            for key, value in possibleTasksForBot.items():
                taskName = key
                if value["tgBOT_check_var"] == "True":
                    markup.add(types.InlineKeyboardButton(taskName, callback_data=str(taskName)))

            logToFile("TG BOT: " + Localize("Commands"))
            message = bot.send_message(chat_id, text=Localize("Commands"), reply_markup=markup)
            asyncio.run(delete_message(chat_id, message.id, 30))

        elif "http" in message or ".ru" in message or ".com" in message:
            message = message.replace(" ", SPACE_SYMBOL)
            launchWithoutConsole(["cmd", "/c", "OpenBrowserLink.vbs " + message])
            bot.send_message(chat_id, text=Localize("Open"))
            logToFile("TG BOT: " + Localize("Open") + " | " + message)
            if showNotifications == "True":
                Notify(Localize("Open") + " | " + message)
        else:
            RunTaskFromTG(message, chat_id)

def BotHandler():
    if TG_TOKEN == "":
        return

    while True:
        try:
            bot.polling(none_stop=False)
        except Exception as err:
            print("Internet error! " + str(err))
#endregion

if __name__ == "__main__":
    alreadyRunning = AlreadyRunning()

    if alreadyRunning and RESTART_ARG in sys.argv:
        # Перезапуск после сохранения настроек: ждём, пока старая копия закроется
        for attempt in range(50):
            sleep(0.2)
            alreadyRunning = AlreadyRunning()
            if not alreadyRunning:
                break

    if alreadyRunning:
        # Уже запущенная копия сама откроет своё окно
        if SignalRunningInstance():
            logToFile(PROGRAM_NAME + " is already running, opened its window, second copy closed")
        else:
            logToFile(PROGRAM_NAME + " is already running, second copy closed")
            with suppress(Exception):
                Notify(PROGRAM_NAME + " is already running")
        ExitProgram()

    ReloadTasks()

    flaskThread = threading.Thread(target=flask_main)
    flaskThread.daemon = True
    flaskThread.start()

    AppServerHandlerThread = threading.Thread(target=AppServerHandler)
    AppServerHandlerThread.daemon = True
    AppServerHandlerThread.start()

    BotThread = threading.Thread(target=BotHandler)
    BotThread.daemon = True
    BotThread.start()

    if CheckWorkURL != "" and os.path.exists("RestartTunnel.vbs"):
        launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])

    if NotifyOnStart == "True":
        # Notify ждёт, пока уведомление скроется, а иконка трея должна появиться сразу
        threading.Thread(target=lambda: Notify(Localize("NotifyOnStartMessage")), daemon=True).start()

    try:
        StartUiServer()

        showRequestsThread = threading.Thread(target=WaitForShowRequests)
        showRequestsThread.daemon = True
        showRequestsThread.start()

        if closeToTrayOnStart != "True" or SHOW_ARG in sys.argv:
            ShowWindow()

        logToFile(Localize("runOn") + " " + str(PORT))

        RunTray()
    except Exception:
        logException("main", *sys.exc_info())
        with suppress(Exception):
            Notify(PROGRAM_NAME + " crashed, see log.txt")
        ExitProgram(1)

    ExitProgram()
