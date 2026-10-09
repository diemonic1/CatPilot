# Уведомления Windows (toast)
import threading
import winreg
from contextlib import suppress

from win11toast import toast

from catpilot_config import ICON, PROGRAM_NAME

NOTIFY_APP_ID_KEY = "Software\\Classes\\AppUserModelId\\" + PROGRAM_NAME

notifyAppIdRegistered = False

def RegisterNotifyAppId():
    """Windows подписывает уведомление по AppUserModelID отправителя; без регистрации
    win11toast шлёт от имени "Python". Ключ в HKCU задаёт имя и иконку в шапке"""
    global notifyAppIdRegistered

    if notifyAppIdRegistered:
        return

    with suppress(OSError):
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, NOTIFY_APP_ID_KEY) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, PROGRAM_NAME)
            winreg.SetValueEx(key, "IconUri", 0, winreg.REG_SZ, ICON)
        notifyAppIdRegistered = True

def ShowToast(message):
    with suppress(Exception):
        RegisterNotifyAppId()
        toast(str(message), icon=ICON, app_id=PROGRAM_NAME)

def Notify(message, wait=False):
    """toast() возвращается только когда уведомление скроется, поэтому по умолчанию
    показываем его в фоне: иначе задача, бот и HTTP-ответ ждали бы его исчезновения.
    wait=True — перед немедленным выходом из программы"""
    if wait:
        ShowToast(message)
    else:
        threading.Thread(target=ShowToast, args=(message,), name="Notify", daemon=True).start()
