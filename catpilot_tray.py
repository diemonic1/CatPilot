# Иконка в трее. Пока программа в трее, кроме pystray (чистый Win32) никакого интерфейса нет:
# окно — отдельный процесс, который создаётся только по «Показать»
import ctypes
from contextlib import suppress

import pystray
from PIL import Image
from pystray import Menu, MenuItem

from catpilot_config import ICON, PROGRAM_NAME
from catpilot_instance import AddShutdownHandler, ExitProgram, QuitProgram
from catpilot_localization import Localize
from catpilot_log import LogToFile
import catpilot_tasks
from catpilot_tasks import StartTaskInBackground, tasksChangedHandlers
from catpilot_tray_icons import TrayItemTextAndBitmap

MIIM_BITMAP = 0x00000080
WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016

trayIcon = None
onShowWindow = None

class TrayIcon(pystray.Icon):
    """pystray.Icon, у пунктов меню которого может быть картинка слева (MenuItem.iconBitmap)"""

    def _create_menu_item(self, descriptor, callbacks):
        menuItem = super()._create_menu_item(descriptor, callbacks)

        bitmap = getattr(descriptor, "iconBitmap", None)
        if bitmap:
            menuItem.fMask |= MIIM_BITMAP
            menuItem.hbmpItem = bitmap

        return menuItem

def TaskMenuItem(task):
    text, bitmap = TrayItemTextAndBitmap(task["name"])
    url = task["url"]
    menuItem = MenuItem(text, lambda: StartTaskInBackground(url))
    menuItem.iconBitmap = bitmap
    return menuItem

def BuildTrayMenu(tasks):
    menuItems = [TaskMenuItem(task) for task in tasks if task["trayCommand"] == "True"]

    menuItems.append(Menu.SEPARATOR)
    menuItems.append(MenuItem(Localize("show"), lambda: onShowWindow(), default=True))
    menuItems.append(MenuItem(Localize("quit"), lambda: QuitProgram()))

    return Menu(*menuItems)

def UpdateTrayMenu(tasks):
    if trayIcon is not None:
        trayIcon.menu = BuildTrayMenu(tasks)

def OnEndSession(wparam, lparam):
    """Windows завершает сеанс. Окно pystray на необработанные сообщения
    отвечает 0, что для WM_QUERYENDSESSION означает запрет выключения,
    поэтому подтверждаем выход и закрываемся сами"""
    if wparam:
        LogToFile("Windows session is ending, closing " + PROGRAM_NAME)
        ExitProgram()
    return 0

def HideTray():
    if trayIcon is not None:
        # visible = False сразу удаляет иконку (NIM_DELETE), иначе после os._exit
        # в трее остаётся «призрак» до наведения мыши
        with suppress(Exception):
            trayIcon.visible = False

def RunTray(showWindow):
    """Блокирует поток до выхода из программы"""
    global trayIcon, onShowWindow

    onShowWindow = showWindow

    # Тёмное контекстное меню трея (SetPreferredAppMode)
    with suppress(Exception):
        ctypes.windll['uxtheme.dll'][135](1)

    icon = TrayIcon(PROGRAM_NAME, Image.open(ICON), PROGRAM_NAME, menu=BuildTrayMenu(catpilot_tasks.loadedTasks))
    icon._message_handlers[WM_QUERYENDSESSION] = lambda wparam, lparam: 1
    icon._message_handlers[WM_ENDSESSION] = OnEndSession

    trayIcon = icon
    tasksChangedHandlers.append(UpdateTrayMenu)
    AddShutdownHandler(HideTray)
    icon.run()
