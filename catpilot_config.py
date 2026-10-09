# Константы программы, пути и Settings.json
import json
import os
import sys

PROGRAM_NAME = "CatPilot"
PROGRAM_VERSION = "2.0.0"

# Папка программы: рядом с CatPilot.exe в сборке или с CatPilot.py при запуске из исходников.
# Все файлы (настройки, задачи, лог, локализации) ищутся относительно неё, а не текущей папки
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

def AppPath(*parts):
    return os.path.join(APP_DIR, *parts)

ICON = AppPath("CatPilot.ico")
SETTINGS_FILE = AppPath("Settings.json")

DEFAULT_PORT = 5000
DEFAULT_SETTINGS = {
    "PORT": DEFAULT_PORT,
    "showNotifications": "True",
    "closeToTrayOnStart": "False",
    "language": "English",
    "AllowedTG_IDs": "",
    "TG_TOKEN": "",
    "CheckWorkURL": "",
    "AdditionalURL": "",
    "AutoStart": "False",
    "NotifyOnStart": "False",
}

# Настройки читаются один раз при старте: после сохранения из окна программа перезапускается
settings = dict(DEFAULT_SETTINGS)

def UseAppDirectory():
    # Пользовательские vbs-скрипты и вспомогательные файлы запускаются с относительными путями,
    # поэтому рабочая папка — папка программы, даже если её запустили ярлыком из другой
    os.chdir(APP_DIR)

def LoadSettings():
    """Читает Settings.json поверх значений по умолчанию; если файла нет — создаёт его.
    Возвращает текст ошибки, если файл повреждён (тогда используются значения по умолчанию)"""
    settings.clear()
    settings.update(DEFAULT_SETTINGS)

    if not os.path.isfile(SETTINGS_FILE):
        SaveSettings(settings)
        return None

    try:
        # utf-8-sig: Блокнот и PowerShell сохраняют UTF-8 с BOM, json.load на нём падает
        with open(SETTINGS_FILE, encoding="utf-8-sig") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Settings.json must contain an object")
    except (OSError, ValueError) as e:
        return "Settings.json read error, defaults are used | " + str(e)

    for key in DEFAULT_SETTINGS:
        if key in data:
            settings[key] = data[key] if key == "PORT" else str(data[key])

    settings["PORT"] = ParsePort(settings["PORT"]) or DEFAULT_PORT
    return None

def SaveSettings(newSettings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(newSettings, file, ensure_ascii=False)

def ParsePort(value):
    try:
        port = int(str(value).strip())
    except ValueError:
        return None
    return port if 1 <= port <= 65535 else None

def IsOn(key):
    return settings.get(key) == "True"

def Setting(key):
    return str(settings.get(key, "")).strip()
