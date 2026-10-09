# Задачи: на диске — пара файлов Tasks\<url>.vbs (скрипт) и Tasks\<url>.settings (json)
import json
import os
import re
import subprocess
import threading
from contextlib import suppress

import pyautogui

from catpilot_config import AppPath, IsOn
from catpilot_localization import Localize
from catpilot_log import LogToFile
from catpilot_notify import Notify

TASKS_DIR = "Tasks"
TASK_FLAGS = ("notify", "tgBOT", "trayCommand")
TASK_BUTTONS = ("button1", "button2", "button3")
NO_BUTTON = "None"
TASK_URL_PATTERN = re.compile("^[a-zA-Z0-9]+$")

BUTTONS = ['None', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
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

tasksLock = threading.Lock()
# Последний прочитанный с диска список; заменяется целиком, поэтому его можно
# читать из других потоков без блокировки
loadedTasks = []
# Вызываются после каждого перечитывания задач (меню трея)
tasksChangedHandlers = []

#region Run
def LaunchWithoutConsole(command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(command, startupinfo=startupinfo).wait()

def RunVbs(path):
    return LaunchWithoutConsole(["cmd", "/c", path])

def PressKeys(keys):
    """Одна клавиша или сочетание: все нажимаются по очереди, затем отпускаются"""
    for key in keys:
        pyautogui.keyDown(key)
    for key in keys:
        pyautogui.keyUp(key)

def IsValidTaskUrl(url):
    return bool(TASK_URL_PATTERN.match(str(url)))

def TaskFilePath(url, extension):
    return os.path.join(TasksFolder(), url + extension)

def StartTask(url):
    url = str(url)

    # URL приходит из сети и подставляется в командную строку cmd, поэтому
    # допускаются только латиница и цифры (как и при сохранении задачи)
    if not IsValidTaskUrl(url):
        message = url + " | " + Localize("fail")
        LogToFile(message)
        return message

    if not os.path.isfile(TaskFilePath(url, ".vbs")):
        message = url + " | " + Localize("fail")
        LogToFile(message)
        Notify(message)
        return message

    try:
        if RunVbs(os.path.join(TASKS_DIR, url + ".vbs")) == 0:
            task = ReadTaskSettings(url)
            result = Localize("success")

            if IsOn("showNotifications") and task.get("notify", "True") == "True":
                Notify(task.get("name", url))

            keys = [task[key] for key in TASK_BUTTONS if task.get(key, NO_BUTTON) in BUTTONS and task[key] != NO_BUTTON]
            if keys:
                PressKeys(keys)
        else:
            result = Localize("fail")
            Notify(url + " | " + result)
    except Exception as e:
        result = str(e)

    message = url + " | " + result
    LogToFile(message)
    return message

def StartTaskInBackground(url):
    # Задача ждёт завершения vbs, а меню трея не должно подвисать
    threading.Thread(target=StartTask, args=(url,), daemon=True).start()
#endregion

#region Files
def TasksFolder():
    folder = AppPath(TASKS_DIR)
    os.makedirs(folder, exist_ok=True)
    return folder

def ReadTaskSettings(url):
    with suppress(OSError, ValueError):
        with open(TaskFilePath(url, ".settings"), "r", encoding="utf-8-sig") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    return {}

def LoadTasks():
    tasks = []

    for filename in sorted(os.listdir(TasksFolder())):
        if not filename.endswith(".vbs"):
            continue

        url = filename[:-4]

        try:
            with open(TaskFilePath(url, ".vbs"), "r", encoding="utf-8-sig") as file:
                script = file.read().rstrip()
        except (OSError, UnicodeDecodeError) as e:
            LogToFile("Task read error: " + filename + " | " + str(e))
            continue

        settingsFromFile = ReadTaskSettings(url)
        task = {"url": url, "script": script, "name": str(settingsFromFile.get("name", url))}

        for key in TASK_BUTTONS:
            task[key] = str(settingsFromFile.get(key, NO_BUTTON))

        for key in TASK_FLAGS:
            task[key] = str(settingsFromFile.get(key, "True"))

        tasks.append(task)

    return tasks

def ValidateTasks(tasks):
    """Возвращает (текст ошибки, индекс задачи) или None"""
    for i, task in enumerate(tasks):
        if task["url"] == "" or task["name"] == "" or task["script"].strip() == "":
            return Localize("emptyError"), i

        if not IsValidTaskUrl(task["url"]):
            return Localize("notAllowedURLError"), i

    for key in ("url", "name"):
        # URL сравниваются без учёта регистра: файлы Windows регистр не различают
        seen = {}
        for i, task in enumerate(tasks):
            value = task[key].lower() if key == "url" else task[key]
            if value in seen:
                return Localize("copyError") + " | " + task[key] + " | №" + str(seen[value] + 1) + ", №" + str(i + 1), i
            seen[value] = i

    return None

def NormalizeTask(raw):
    if not isinstance(raw, dict):
        raw = {}

    task = {"url": str(raw.get("url", "")).strip(),
            "name": str(raw.get("name", "")).strip(),
            "script": str(raw.get("script", "")).replace("\r\n", "\n")}

    for key in TASK_BUTTONS:
        value = str(raw.get(key, NO_BUTTON))
        task[key] = value if value in BUTTONS else NO_BUTTON

    for key in TASK_FLAGS:
        task[key] = "True" if str(raw.get(key, "True")) == "True" else "False"

    return task

def SaveTasks(rawTasks):
    """Возвращает (текст ошибки, индекс задачи) или None"""
    tasks = [NormalizeTask(raw) for raw in rawTasks]

    error = ValidateTasks(tasks)
    if error is not None:
        return error

    with tasksLock:
        folder = TasksFolder()
        existing = os.listdir(folder)
        keep = set()

        # Сначала записываем новые файлы и только потом удаляем лишние:
        # ошибка записи на полпути не должна стереть все задачи
        for task in tasks:
            # Перезапись файла в Windows сохраняет старый регистр имени, а он и есть URL
            for extension in (".vbs", ".settings"):
                fileName = task["url"] + extension
                for oldName in existing:
                    if oldName.lower() == fileName.lower() and oldName != fileName:
                        os.remove(os.path.join(folder, oldName))

            with open(TaskFilePath(task["url"], ".vbs"), "w", encoding="utf-8") as file:
                file.write(task["script"].rstrip() + "\n")

            settingsForFile = {key: task[key] for key in TASK_BUTTONS + ("name",) + TASK_FLAGS}
            with open(TaskFilePath(task["url"], ".settings"), "w", encoding="utf-8") as file:
                json.dump(settingsForFile, file, ensure_ascii=False)

            keep.add((task["url"] + ".vbs").lower())
            keep.add((task["url"] + ".settings").lower())

        for filename in os.listdir(folder):
            if filename.endswith((".vbs", ".settings")) and filename.lower() not in keep:
                os.remove(os.path.join(folder, filename))

    ReloadTasks()
    return None

def DeleteTaskFiles(url):
    if not IsValidTaskUrl(url):
        return False

    with tasksLock:
        for extension in (".vbs", ".settings"):
            path = TaskFilePath(url, extension)
            if os.path.isfile(path):
                os.remove(path)

    ReloadTasks()
    return True

def ReloadTasks():
    """Перечитывает задачи с диска и обновляет всё, что от них зависит"""
    global loadedTasks

    tasks = LoadTasks()
    loadedTasks = tasks

    for handler in tasksChangedHandlers:
        with suppress(Exception):
            handler(tasks)

    return tasks

def FindTask(nameOrUrl):
    """Задача по названию или URL из последнего прочитанного списка"""
    for task in loadedTasks:
        if task["name"] == nameOrUrl:
            return task
    for task in loadedTasks:
        if task["url"] == nameOrUrl:
            return task
    return None
#endregion
