# Локализации из папки Localization: <язык>.json со словарём ключ -> текст
import json
import os

from catpilot_config import AppPath, settings
from catpilot_log import LogToFile
from catpilot_notify import Notify

DEFAULT_LANGUAGE = "English"

languagesList = []
localizationDict = {}
missingKeys = set()

def LoadLocalizations():
    languagesList.clear()
    localizationDict.clear()
    folder = AppPath("Localization")

    if os.path.isdir(folder):
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".json"):
                continue
            try:
                with open(os.path.join(folder, filename), "r", encoding="utf-8-sig") as file:
                    localizationDict[filename[:-5]] = json.load(file)
                languagesList.append(filename[:-5])
            except (OSError, ValueError) as e:
                LogToFile("Localization file error: " + filename + " | " + str(e))

    if not languagesList:
        languagesList.append(DEFAULT_LANGUAGE)

def CurrentLanguage():
    language = settings.get("language", DEFAULT_LANGUAGE)
    return language if language in localizationDict else DEFAULT_LANGUAGE

def Localize(key):
    """Текст на выбранном языке; если ключа нет — английский, если нет и его — сам ключ"""
    for language in (CurrentLanguage(), DEFAULT_LANGUAGE):
        text = localizationDict.get(language, {}).get(key)
        if text is not None:
            return text

    # Сообщаем один раз на ключ: Localize вызывается часто (меню трея, бот, каждая задача)
    if key not in missingKeys:
        missingKeys.add(key)
        message = 'Not find language "' + CurrentLanguage() + '" or key "' + key + '" in localization'
        LogToFile(message)
        Notify(message)
    return key

def UiStrings():
    strings = dict(localizationDict.get(DEFAULT_LANGUAGE, {}))
    strings.update(localizationDict.get(CurrentLanguage(), {}))
    return strings
