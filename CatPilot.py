from time import sleep

import customtkinter
from customtkinter import *
import tkinter as tk
from tkinter.messagebox import askyesno
from contextlib import suppress
from enum import Enum, auto
from typing import Any, Callable
from tkinter.scrolledtext import ScrolledText
import psutil

import ctypes
import difflib
import re
import pyautogui
import time
import telebot
from telebot import types
from requests import get
import requests.exceptions
import threading
from flask import Flask
from datetime import datetime
from pystray import MenuItem as item, Menu
import pystray
from PIL import Image
import subprocess
import os
from win11toast import toast
import asyncio
import json
import sys
import werkzeug

PROGRAM_NAME = "CatPilot"
ICON_RAW = "CatPilot.ico"
ICON = os.getcwd() + "\\" + ICON_RAW

COMMANDS_TO_START_BOT = "/start /help /commands /начать /помощь /команды"

STAR_ICON = "*"
SPACE_SYMBOL = "%20"

RED_COLOR = "#b31e1e"
RED_HOVER_COLOR = "#6b1616"
REG_HIGH_COLOR = "#ff4d4d"
WHITE_GREY_COLOR = "#8f8f8f"

GREEN_COLOR = "#22ba20"
GREEN_HOVER_COLOR = "#177515"
BACKGROUND_COLOR = "#242424"
FOREGROUND_COLOR = "#2b2b2b"

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
#endregion

#region Notify
async def NotifyAsync(message):
    toast(message, PROGRAM_NAME, icon=ICON)

def Notify(message):
    asyncio.run(NotifyAsync(message))
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

#region get_windows_scaling

def get_windows_scaling():
    try:
        # Для Windows 8.1 и выше
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except:
        # Для более старых версий Windows
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            LOGPIXELSX = 88
            scale_factor = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX) / 96
            ctypes.windll.user32.ReleaseDC(0, hdc)
        except:
            scale_factor = 1.0
    return scale_factor

#endregion

#region MultiColumnDropdown

class MultiColumnDropdown(customtkinter.CTkToplevel):
    def __init__(self, master, selected_option, options, columns, select_callback, width=100, height=200):
        super().__init__(master)
        self.selected_option = selected_option
        self.select_callback = select_callback
        self.columns = columns

        # Настройки окна
        self.overrideredirect(True)  # Убираем рамки окна
        self.attributes("-topmost", True)  # Поверх всех окон
        self.geometry(f"{width}x{height}")

        # Создаем скроллируемый фрейм
        self.scroll_frame = customtkinter.CTkScrollableFrame(self, width=width - 20, height=height - 20)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Создаем кнопки опций
        self.create_options(options)

        # Привязываем события для закрытия при клике вне окна
        self.bind("<FocusOut>", lambda e: self.destroy())

    def create_options(self, options):
        """Создает кнопки опций в несколько столбцов"""
        for i, option in enumerate(options):
            row = i // self.columns
            col = i % self.columns

            btn = customtkinter.CTkButton(
                self.scroll_frame,
                text=option,
                bg_color=FOREGROUND_COLOR,
                width=100,
                fg_color= GREEN_COLOR if option == self.selected_option.get() else BACKGROUND_COLOR,
                command=lambda opt=option: self.select_option(opt)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

        # Настраиваем равномерное распределение столбцов
        for col in range(self.columns):
            self.scroll_frame.grid_columnconfigure(col, weight=1)

    def select_option(self, option):
        """Выбирает опцию и закрывает окно"""
        self.select_callback(option)
        self.destroy()

class MultiColumnOptionMenu(customtkinter.CTkFrame):
    def __init__(self, master, options, _on_mousewheel, default_option, columns=5, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.selected_option = customtkinter.StringVar(value=default_option)
        self.options = options
        self.columns = columns

        # Основная кнопка для отображения выбранного значения
        self.main_button = customtkinter.CTkButton(
            self,
            textvariable=self.selected_option,
            command=self.show_dropdown,
            width=100,
            bg_color=FOREGROUND_COLOR,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870")
        )
        self.main_button.configure(fg_color=(("#3B8ED0", "#1F6AA5")) if self.selected_option.get() != "None" else ((BACKGROUND_COLOR, BACKGROUND_COLOR)))
        self.main_button.pack()
        self.main_button.bind("<MouseWheel>", _on_mousewheel)

        # Текущее выпадающее окно
        self.dropdown_window = None

    def show_dropdown(self):
        """Показывает выпадающее окно"""
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.dropdown_window.destroy()
            return

        # Позиционируем окно под кнопкой
        x = self.winfo_rootx() - 420
        y = self.winfo_rooty() + self.main_button.winfo_height()

        self.dropdown_window = MultiColumnDropdown(
            master=self.winfo_toplevel(),
            options=self.options,
            columns=self.columns,
            selected_option=self.selected_option,
            select_callback=self.select_option,
            width=520,
            height=400
        )
        self.dropdown_window.geometry(f"+{x}+{y}")
        self.dropdown_window.focus_set()

    def select_option(self, option):
        """Выбирает опцию и обновляет основную кнопку"""
        self.selected_option.set(option)
        self.main_button.configure(fg_color=(("#3B8ED0", "#1F6AA5")) if self.selected_option.get() != "None" else ((BACKGROUND_COLOR, BACKGROUND_COLOR)))
        if self.command:
            self.command(option)

    def get(self):
        return self.selected_option.get()

#endregion

#region SimpleLineNumberedTextbox

class SimpleLineNumberedTextbox(customtkinter.CTkFrame):
    onHover = False

    def __init__(self, master, parent, **kwargs):
        super().__init__(master, **kwargs)

        self.line_number = customtkinter.CTkTextbox(self, width=25, text_color=WHITE_GREY_COLOR, fg_color="#1d1e1e",
                                                    wrap="none", corner_radius=0, pady=7, border_spacing=0,
                                                    activate_scrollbars=False, font=("Helvetika", 17), height=210)

        self.textbox = customtkinter.CTkTextbox(self, wrap="none", corner_radius=0, pady=7, border_spacing=0, fg_color="#1d1e1e",
                                                width=960, height=210, font=("Helvetika", 17), text_color="#ffffff")

        self.line_number.pack(side="left", fill="both", expand=True)
        self.textbox.pack(side="left", fill="both", expand=True)

        self.textbox.bind("<Enter>", lambda e: self.on_enter(e))
        self.textbox.bind("<Leave>", lambda e: self.on_leave(e))
        self.line_number.bind("<Enter>", lambda e: self.on_enter(e))
        self.line_number.bind("<Leave>", lambda e: self.on_leave(e))

        self.line_number.bind("<MouseWheel>", lambda e: "break")

        self.textbox.bind("<KeyRelease>", self._update_line_numbers)
        self.textbox.bind("<KeyRelease>", self._update_comments)
        self.textbox.bind("<KeyRelease>", parent.typing)

        self.line_number.bind("<B1-Motion>", lambda e: "break")
        self.line_number.bind("<ButtonPress-1>", lambda e: "break")  # Нажатие левой кнопки
        self.line_number.bind("<Shift-Button-1>", lambda e: "break")  # Выделение с Shift
        self.line_number.bind("<Control-Button-1>", lambda e: "break")  # Выделение с Ctrl

        current_scrollcmd = self.textbox._textbox.cget("yscrollcommand")

        # Проверяем тип и сохраняем оригинальную команду
        if callable(current_scrollcmd ):
            self._original_scrollcmd = current_scrollcmd
        elif isinstance(current_scrollcmd , str):
            # Для строковых команд создаем обертку через tcl
            self._original_scrollcmd = lambda *args: self.textbox._textbox.tk.call(current_scrollcmd, *args)
        else:
            self._original_scrollcmd = None

        # Устанавливаем нашу прокси-функцию
        self.textbox.configure(yscrollcommand=self.yscroll)

        self._update_line_numbers()

    def _update_line_numbers(self, withScroll=None, event=None):
        linesCount = len(self.textbox.get("1.0", "end-1c").split("\n"))
        self.line_number.configure(state="normal")
        self.line_number.delete("1.0", "end")
        self.line_number.insert("1.0", "\n".join(str(i) for i in range(1, linesCount + 1)))
        self.line_number.tag_config("right", justify="right")
        self.line_number.tag_add("right", "1.0", "end")
        self.line_number.configure(state="disabled")
        first, last = self.textbox.yview()
        self.line_number.yview_moveto(first)

    def _update_comments(self, event=None):
        lines = self.textbox.get("1.0", "end-1c").split("\n")
        for i in range(len(lines)):
            if len(lines[i]) > 0 and "'" in lines[i]:
                ind = lines[i].index("'")
                self.textbox.tag_add("t" + str(i+1), str(i+1) + '.' + str(ind), str(i+1) + '.end lineend')
                self.textbox.tag_config("t" + str(i+1), foreground=GREEN_COLOR)

    def insert(self, text):
        self.textbox.insert(tk.INSERT, text)

    def yscroll(self, *args):
        first, last = self.textbox.yview()
        self.line_number.yview_moveto(first)
        self._original_scrollcmd(*args)

    def on_enter(self, event):
        # Запускаем функцию при наведении
        global hover_job
        hover_job = self.after(1, self.repeat_while_hovering)  # 100ms задержка

    def on_leave(self, event):
        # Останавливаем функцию при уходе курсора
        global hover_job
        if hover_job:
            self.after_cancel(hover_job)
            hover_job = None

    def repeat_while_hovering(self):
        global hover_job
        first, last = self.textbox.yview()
        self.line_number.yview_moveto(first)
        # Планируем следующий вызов
        hover_job = self.after(1, self.repeat_while_hovering)

    def get(self, arg1, arg2):
        return self.textbox.get(arg1, arg2)

#endregion

#region Tooltip

class ToolTipStatus(Enum):
    OUTSIDE = auto()
    INSIDE = auto()
    VISIBLE = auto()

class Binding:
    def __init__(self, widget: tk.Widget, binding_name: str, functor: Callable) -> None:
        self._widget = widget
        self._name: str = binding_name
        self._id: str = self._widget.bind(binding_name, functor, add="+")

    def unbind(self) -> None:
        self._widget.unbind(self._name, self._id)

class ToolTip(tk.Toplevel):
    DEFAULT_PARENT_KWARGS = {"bg": "black", "padx": 1, "pady": 1}
    DEFAULT_MESSAGE_KWARGS = {"aspect": 1000}
    S_TO_MS = 1000

    def __init__(
        self,
        widget: tk.Widget,
        msg: str,
        delay: float = 0.0,
        follow: bool = True,
        refresh: float = 1.0,
        x_offset: int = +10,
        y_offset: int = +10,
        parent_kwargs: dict or None = None,
        **message_kwargs: Any,
    ):
        self.widget = widget
        # ToolTip should have the same parent as the widget unless stated
        # otherwise in the `parent_kwargs`
        tk.Toplevel.__init__(self, **(parent_kwargs or self.DEFAULT_PARENT_KWARGS))
        self.withdraw()  # Hide initially in case there is a delay
        # Disable ToolTip's title bar
        self.overrideredirect(True)

        # StringVar instance for msg string|function
        self.msg_var = tk.StringVar()
        self.msg = msg
        self._update_message()
        self.delay = delay
        self.follow = follow
        self.refresh = refresh
        self.x_offset = x_offset
        self.y_offset = y_offset
        # visibility status of the ToolTip inside|outside|visible
        self.status = ToolTipStatus.OUTSIDE
        self.last_moved = 0.0
        # use Message widget to host ToolTip
        self.message_kwargs: dict = self.DEFAULT_MESSAGE_KWARGS.copy()
        self.message_kwargs.update(message_kwargs)
        self.message_widget = tk.Message(
            self,
            textvariable=self.msg_var,
            **self.message_kwargs,
        )
        self.message_widget.grid()
        self.bindigs = self._init_bindings()

    def _init_bindings(self) -> list[Binding]:
        bindings = [
            Binding(self.widget, "<Enter>", self.on_enter),
            Binding(self.widget, "<Leave>", self.on_leave),
            Binding(self.widget, "<ButtonPress>", self.on_leave),
        ]
        if self.follow:
            bindings.append(
                Binding(self.widget, "<Motion>", self._update_tooltip_coords)
            )
        return bindings

    def destroy(self) -> None:
        """Destroy the ToolTip and unbind all the bindings."""
        with suppress(tk.TclError):
            for b in self.bindigs:
                b.unbind()
            self.bindigs.clear()
            super().destroy()

    def on_enter(self, event: tk.Event) -> None:
        """
        Processes motion within the widget including entering and moving.
        """
        self.last_moved = time.perf_counter()
        self.status = ToolTipStatus.INSIDE
        self._update_tooltip_coords(event)
        self.after(int(self.delay * self.S_TO_MS), self._show)

    def on_leave(self, event: tk.Event or None = None) -> None:
        """
        Hides the ToolTip.
        """
        self.status = ToolTipStatus.OUTSIDE
        self.withdraw()

    def _update_tooltip_coords(self, event: tk.Event) -> None:
        """
        Updates the ToolTip's position.
        """
        self.geometry(f"+{event.x_root + self.x_offset}+{event.y_root + self.y_offset}")

    def _update_message(self) -> None:
        """Update the message displayed in the tooltip."""
        if callable(self.msg):
            msg = self.msg()
            if isinstance(msg, list):
                msg = "\n".join(msg)
        elif isinstance(self.msg, str):
            msg = self.msg
        elif isinstance(self.msg, list):
            msg = "\n".join(self.msg)
        else:
            raise TypeError(
                f"ToolTip `msg` must be a string, list of strings, or a "
                f"callable returning them, not {type(self.msg)}."
            )
        self.msg_var.set(msg)

    def _show(self) -> None:
        """
        Displays the ToolTip.

        Recursively queues `_show` in the scheduler every `self.refresh` seconds
        """
        if (
            self.status == ToolTipStatus.INSIDE
            and time.perf_counter() - self.last_moved >= self.delay
        ):
            self.status = ToolTipStatus.VISIBLE

        if self.status == ToolTipStatus.VISIBLE:
            self._update_message()
            self.deiconify()

            # Recursively call _show to update ToolTip with the newest value of msg
            # This is a race condition which only exits when upon a binding change
            # that in turn changes the `status` to outside
            self.after(int(self.refresh * self.S_TO_MS), self._show)

#endregion

#region Window
possibleTasksForBot = {}

class SettingsWindow(customtkinter.CTkToplevel):
    def SaveSettings(self, port_s, notify_s, tray_s, language, AllowedTG_IDs_s, TG_TOKEN_s, CheckWorkURL_s, AdditionalURL_s, AutoStart_s, NotifyOnStart_s):
        file = open('Settings.json', 'w', encoding='utf-8')
        file.write(
            '{ "PORT": ' + str(port_s) + ', "showNotifications": "'
            + str(notify_s) + '", "closeToTrayOnStart": "' + str(tray_s) + '", "language": "'
            + str(language) + '", "AllowedTG_IDs": "' + str(AllowedTG_IDs_s).rstrip() + '", "TG_TOKEN": "'
            + str(TG_TOKEN_s).rstrip() + '", "CheckWorkURL": "' + str(CheckWorkURL_s).rstrip() + '", "AdditionalURL": "'
            + str(AdditionalURL_s).rstrip() + '", "AutoStart": "'
            + str(AutoStart_s).rstrip() + '", "NotifyOnStart": "' + str(NotifyOnStart_s) + '" }')
        file.close()

        if str(AutoStart_s) == "True":
            launchWithoutConsole(["cmd", "/c", "LoadOnStartup.vbs"])
        else:
            launchWithoutConsole(["cmd", "/c", "NotLoadOnStartup.bat"])

        UpdateSettings()
        self.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def __init__(self, parent):
        global languagesList
        super().__init__(parent)
        self.geometry('1270x790')
        self.title(Localize("settings"))
        self.after(210, lambda: self.iconbitmap(ICON))

        variable = customtkinter.StringVar(self)
        variable.set(str(LANGUAGE))

        CTkLabel(self, text=Localize("GeneralSettings"), text_color=GREEN_COLOR).grid(row=0, column=0, pady=10, padx=20)

        CTkLabel(self, text=Localize("language"), text_color="#ffffff").grid(row=1, column=0, pady=10, padx=20)
        opt = customtkinter.CTkOptionMenu(self, values=languagesList, variable=variable)
        opt.configure(width=15, font=("Arial", 12))
        opt.grid(sticky="W", row=1, column=1)

        portlabel = CTkLabel(self, text='PORT', text_color="#ffffff")
        portlabel.grid(row=2, column=0, pady=10, padx=20)
        port_s = CTkEntry(self, width=150, font=("Arial", 14))
        port_s.grid(sticky="W", row=2, column=1)
        port_s.insert(0, str(PORT))
        ToolTip(portlabel, msg=Localize("portTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(port_s, msg=Localize("portTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        notifyLabel = CTkLabel(self, text=Localize("notify"), text_color="#ffffff")
        notifyLabel.grid(row=3, column=0, pady=10, padx=20)
        notify_check_var = customtkinter.StringVar(value=str(showNotifications))
        notify_checkbox = customtkinter.CTkCheckBox(self, text="",
                                             variable=notify_check_var, onvalue="True", offvalue="False")
        notify_checkbox.grid(sticky="W", row=3, column=1)
        ToolTip(notifyLabel, msg=Localize("notifyTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(notify_checkbox, msg=Localize("notifyTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        traySettingLabel = CTkLabel(self, text=Localize("traySetting"), text_color="#ffffff")
        traySettingLabel.grid(row=4, column=0, pady=10, padx=20)
        traySetting_check_var = customtkinter.StringVar(value=str(closeToTrayOnStart))
        traySetting_checkbox = customtkinter.CTkCheckBox(self, text="",
                                             variable=traySetting_check_var, onvalue="True", offvalue="False")
        traySetting_checkbox.grid(sticky="W", row=4, column=1)
        ToolTip(traySettingLabel, msg=Localize("traySettingTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(traySetting_checkbox, msg=Localize("traySettingTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        RunAtStartLabel = CTkLabel(self, text=Localize("RunAtStart"), text_color="#ffffff")
        RunAtStartLabel.grid(row=5, column=0, pady=10, padx=20)
        RunAtStart_check_var = customtkinter.StringVar(value=str(AutoStart))
        RunAtStart_checkbox = customtkinter.CTkCheckBox(self, text="",
                                             variable=RunAtStart_check_var, onvalue="True", offvalue="False")
        RunAtStart_checkbox.grid(sticky="W", row=5, column=1)
        ToolTip(RunAtStartLabel, msg=Localize("AutoStart"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(RunAtStart_checkbox, msg=Localize("AutoStart"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        NotifyOnStartLabel = CTkLabel(self, text=Localize("NotifyOnStart"), text_color="#ffffff")
        NotifyOnStartLabel.grid(row=6, column=0, pady=10, padx=20)
        NotifyOnStart_check_var = customtkinter.StringVar(value=str(NotifyOnStart))
        NotifyOnStart_checkbox = customtkinter.CTkCheckBox(self, text="",
                                             variable=NotifyOnStart_check_var, onvalue="True", offvalue="False")
        NotifyOnStart_checkbox.grid(sticky="W", row=6, column=1)
        ToolTip(NotifyOnStartLabel, msg=Localize("NotifyOnStartToolTip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(NotifyOnStart_checkbox, msg=Localize("NotifyOnStartToolTip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        CTkLabel(self, text=Localize("SettingsBot"), text_color=GREEN_COLOR).grid(row=7, column=0, pady=10, padx=20)

        BOTtokenLabel = CTkLabel(self, text='BOT token', text_color="#ffffff")
        BOTtokenLabel.grid(row=8, column=0, pady=10, padx=20)
        TG_TOKEN_s = CTkEntry(self, width=400, font=("Arial", 14))
        TG_TOKEN_s.grid(sticky="W", row=8, column=1)
        TG_TOKEN_s.insert(0, str(TG_TOKEN))
        ToolTip(BOTtokenLabel, msg=Localize("BOTtokenTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(TG_TOKEN_s, msg=Localize("BOTtokenTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        AllowedTG_IDsLabel = CTkLabel(self, text=Localize("AllowedTG_IDs"), text_color="#ffffff")
        AllowedTG_IDsLabel.grid(row=9, column=0, pady=10, padx=20)
        AllowedTG_IDs_s = CTkEntry(self, width=500, font=("Arial", 14))
        AllowedTG_IDs_s.grid(sticky="W", row=9, column=1)
        AllowedTG_IDs_s.insert(0, str(AllowedTG_IDs))
        ToolTip(AllowedTG_IDsLabel, msg=Localize("AllowedTG_IDsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(AllowedTG_IDs_s, msg=Localize("AllowedTG_IDsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        CTkLabel(self, text=Localize("AdditionalSettings"), text_color=GREEN_COLOR).grid(row=10, column=0, pady=10, padx=20)

        CheckWorkURLLabel = CTkLabel(self, text=Localize("CheckWorkURLLabel"), text_color="#ffffff")
        CheckWorkURLLabel.grid(row=11, column=0, pady=10, padx=20)
        CheckWorkURLEntry = CTkEntry(self, width=400, font=("Arial", 14))
        CheckWorkURLEntry.grid(sticky="W", row=11, column=1)
        CheckWorkURLEntry.insert(0, str(CheckWorkURL))

        ToolTip(CheckWorkURLLabel, msg=Localize("CheckWorkURLTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(CheckWorkURLEntry, msg=Localize("CheckWorkURLTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        AdditionalURLLabel = CTkLabel(self, text=Localize("AdditionalURLLabel"), text_color="#ffffff")
        AdditionalURLLabel.grid(row=12, column=0, pady=10, padx=20)
        AdditionalURLEntry = CTkEntry(self, width=400, font=("Arial", 14))
        AdditionalURLEntry.grid(sticky="W", row=12, column=1)
        AdditionalURLEntry.insert(0, str(AdditionalURL))

        ToolTip(AdditionalURLLabel, msg=Localize("AdditionalURLTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(AdditionalURLEntry, msg=Localize("AdditionalURLTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        customtkinter.CTkLabel(self, text=Localize("afterSave1") + " " + PROGRAM_NAME + " " + Localize("afterSave2"), text_color=REG_HIGH_COLOR, font=("Arial", 14))\
            .grid(row=13, column=0, pady=10, padx=20)

        saveButton = customtkinter.CTkButton(self, text=Localize('saveAll'), command= lambda: self.SaveSettings(port_s.get(),
                                                                                                   notify_check_var.get(), traySetting_check_var.get(),
                                                                                                   variable.get(),
                                                                                                   AllowedTG_IDs_s.get(), TG_TOKEN_s.get(), CheckWorkURLEntry.get(), AdditionalURLEntry.get(),
                                                                                                   RunAtStart_check_var.get(), NotifyOnStart_check_var.get()))
        saveButton.grid(row=14, column=0, pady=10, padx=20)
        ToolTip(saveButton, msg=Localize("saveButtonTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

class LogWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('1200x700')
        self.title(Localize('log'))
        self.after(210, lambda: self.iconbitmap(ICON))
        file = open("log.txt", "r", encoding='utf-8')
        content = file.read()
        file.close()

        text_area = CTkTextbox(self, font=("Helvetika", 15))

        text_area.pack(fill='both', expand=True, pady=10, padx=10)

        text_area.insert(tk.INSERT, content)

        lines = text_area.get("1.0", "end-1c").split("\n")
        for i in range(len(lines)):
            if len(lines[i]) > 0:
                ind = lines[i].index("|")
                text_area.tag_add("t" + str(i+1), str(i+1) + '.0', str(i+1) + '.' + str(ind+1))
                text_area.tag_config("t" + str(i+1), foreground=WHITE_GREY_COLOR)

        text_area.configure(state='disabled')

class AppWindow(customtkinter.CTk):
    allTasksUI = []
    saveButton = None
    labelStringNumber = None
    myCanvas = None
    lastNumber = 0

    # region Tray
    def quit_window(self, icon, item):
        icon.stop()
        self.destroy()

    def show_window(self, icon, item):
        icon.stop()
        self.after(0, self.deiconify)

    def start_task_from_tray(self, url):
        return lambda: StartTask(url)

    def withdraw_window(self):
        ctypes.windll['uxtheme.dll'][135](1)

        self.withdraw()

        image = Image.open(ICON_RAW)

        menuItems = ()

        for task in self.allTasksUI:
            if task["trayCommand_check_var"].get() == "True":
                name = task["nameEntry"].get()
                url = task["urlEntry"].get()
                menuItems = menuItems + (item(name, self.start_task_from_tray(url)),)

        menuItems = menuItems + (Menu.SEPARATOR,)
        menuItems = menuItems + (item(Localize("show"), self.show_window),)
        menuItems = menuItems + (item(Localize("quit"), self.quit_window),)

        icon = pystray.Icon(PROGRAM_NAME, image, PROGRAM_NAME, menu=menuItems)
        icon.run()

    # endregion

    def open_SettingsWindow(self):
        window = SettingsWindow(self)
        window.grab_set()

    def open_LogWindow(self):
        window = LogWindow(self)
        window.grab_set()

    def typing(self, args):
        if self.saveButton._text[-1] != STAR_ICON:
            self.saveButton.configure(fg_color=RED_COLOR, hover_color=RED_HOVER_COLOR, text=self.saveButton._text + " " + STAR_ICON)

    def onFrameConfigure(self, event):
        self.myCanvas.configure(scrollregion=self.myCanvas.bbox("all"))

    def ReadSavedTasks(self):
        fileNames = []
        setiingsFiles = {}

        for filename in os.listdir(os.getcwd() + "\\Tasks"):
            f = os.path.join(os.getcwd() + "\\Tasks", filename)
            if os.path.isfile(f) and ".vbs" in filename:
                fileNames.append(filename)
            elif os.path.isfile(f) and ".settings" in filename:
                setiingsFiles[str(filename)[:-9] + ".vbs"] = filename

        for i in range(len(fileNames)):
            file = open(os.getcwd() + "\\Tasks\\" + fileNames[i], "r", encoding='utf-8')
            content = file.read()
            file.close()

            file = open(os.getcwd() + "\\Tasks\\" + setiingsFiles[fileNames[i]], "r", encoding='utf-8')
            settingsFromFile = json.loads(str(file.read()))
            file.close()

            self.AddTaskUI(str((fileNames[i])[:-4]).replace(SPACE_SYMBOL, " "), content, settingsFromFile, i)

    def Save(self):
        filesToDelete = []

        for i in range(len(self.allTasksUI)):
            url = str(self.allTasksUI[i]["urlEntry"].get()).replace(" ", SPACE_SYMBOL)
            name = str(self.allTasksUI[i]["nameEntry"].get()).replace(" ", SPACE_SYMBOL)
            script = self.allTasksUI[i]["script"].get("1.0", customtkinter.END)

            if url == "" or script == "" or name == "":
                Notify(Localize("emptyError") + " | №" + str(i + 1))
                return

            if not re.match("^[a-zA-Z0-9]+$", url):
                Notify(Localize("notAllowedURLError") + " | №" + str(i + 1))
                return

        for i in range(len(self.allTasksUI)):
            for j in range(len(self.allTasksUI)):
                if self.allTasksUI[i]["urlEntry"].get() == self.allTasksUI[j]["urlEntry"].get() and i != j:
                    Notify(Localize("copyError") + " | " + self.allTasksUI[i]["urlEntry"].get() + " | №" + str(i + 1) + ", №" + str(j + 1))
                    return
                if self.allTasksUI[i]["nameEntry"].get() == self.allTasksUI[j]["nameEntry"].get() and i != j:
                    Notify(Localize("copyError") + " | " + self.allTasksUI[i]["nameEntry"].get() + " | №" + str(i + 1) + ", №" + str(j + 1))
                    return

        for filename in os.listdir(os.getcwd() + "\\Tasks"):
                f = os.path.join(os.getcwd() + "\\Tasks", filename)
                if (os.path.isfile(f) and ".vbs" in filename) or (os.path.isfile(f) and ".settings" in filename):
                    filesToDelete.append(filename)

        for file in filesToDelete:
            os.remove(os.getcwd() + "\\Tasks\\" + file)

        possibleTasksForBot.clear()

        for i in self.allTasksUI:
            url = str(i["urlEntry"].get()).replace(" ", SPACE_SYMBOL)
            script = i["script"].get("1.0", customtkinter.END)
            file = open("Tasks\\" + url + '.vbs', 'w', encoding='utf-8')
            file.write(script)
            file.close()

            file = open("Tasks\\" + url + '.settings', 'w', encoding='utf-8')
            file.write('{ "button1": "' + i["buttons"][0].get() + '", "button2": "' + i["buttons"][1].get() + '", "button3": "' + i["buttons"][2].get() + '", "name": "' + i["nameEntry"].get() + '", "notify": "' + i["notify_check_var"].get() + '", "tgBOT": "' + i["tgBOT_check_var"].get() + '", "trayCommand": "' + i["trayCommand_check_var"].get() + '" }')
            file.close()

            possibleTasksForBot[i["nameEntry"].get()] = {"urlEntry": i["urlEntry"].get(), "tgBOT_check_var": i["tgBOT_check_var"].get()}

        if self.saveButton._text[-1] == STAR_ICON:
            self.saveButton.configure(fg_color=RED_COLOR, hover_color=RED_HOVER_COLOR, text=Localize("save"))

        self.saveButton.configure(fg_color=GREEN_COLOR, hover_color=GREEN_HOVER_COLOR)

    def DeleteTask(self, name, frame):
        if name != "":
            result = askyesno(title=Localize("DeleteTaskQ"), message=Localize("DeleteTaskQ"))
            if result:
                finded = False

                for filename in os.listdir(os.getcwd() + "\\Tasks"):
                    f = os.path.join(os.getcwd() + "\\Tasks\\", filename)
                    if os.path.isfile(f) and name + ".vbs" in filename:
                        finded = True

                if finded:
                    os.remove(os.getcwd() + "\\Tasks\\" + name + ".vbs")

                finded = False

                for filename in os.listdir(os.getcwd() + "\\Tasks"):
                    f = os.path.join(os.getcwd() + "\\Tasks\\", filename)
                    if os.path.isfile(f) and name + ".settings" in filename:
                        finded = True

                if finded:
                    os.remove(os.getcwd() + "\\Tasks\\" + name + ".settings")
            else:
                return

            for widget in self.frame.winfo_children():
                if widget == frame:
                    for task in self.allTasksUI:
                        if task["urlEntry"].get() == name:
                            self.allTasksUI.remove(task)
                            break
                    widget.destroy()

    def AddTaskUI(self, taskURL, scriptText, settingsFromFile, number):
        if settingsFromFile == None:
            settingsFromFile = { "button1": "None", "button2": "None", "button3": "None", "name": "Test" }

        frame = CTkFrame(self.frame, bg_color="transparent", fg_color=FOREGROUND_COLOR)

        leftFrame = CTkFrame(frame, bg_color="transparent", fg_color=FOREGROUND_COLOR)

        scNumber = CTkLabel(leftFrame, text=Localize("scNumber") + str(number + 1), font=("Arial", 17), text_color="#ffffff")
        URLlabel = CTkLabel(leftFrame, text=Localize("URL"), font=("Arial", 17), text_color="#ffffff")
        Namelabel = CTkLabel(leftFrame, text=Localize("Name"), font=("Arial", 17), text_color="#ffffff")

        leftFrame.grid(row=0, column=0, pady=3, padx=5)

        scNumber.grid(row=0, column=0, pady=35, padx=5)
        URLlabel.grid(row=1, column=0, pady=1, padx=5)
        Namelabel.grid(row=2, column=0, pady=1, padx=5)

        urlEntry = CTkEntry(leftFrame, width=200, font=("Arial", 18))
        urlEntry.grid(row=1, column=1, pady=1, padx=5)
        urlEntry.bind('<KeyRelease>', self.typing)
        urlEntry.bind("<MouseWheel>", self._on_mousewheel)
        ToolTip(urlEntry, msg=Localize("urlTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        if taskURL != "":
            urlEntry.insert(0, taskURL)
        else:
            urlEntry.insert(0, "Test")

        nameEntry = CTkEntry(leftFrame, width=200, font=("Arial", 18))
        nameEntry.grid(row=2, column=1, pady=1, padx=5)
        nameEntry.bind('<KeyRelease>', self.typing)
        nameEntry.bind("<MouseWheel>", self._on_mousewheel)
        nameEntry.insert(0, settingsFromFile["name"])
        ToolTip(nameEntry, msg=Localize("nameTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        notifyLabel = CTkLabel(leftFrame, text=Localize("Notify"), font=("Arial", 17), text_color="#ffffff")
        notifyLabel.grid(row=3, column=0, pady=1, padx=5)

        notify_check_var = customtkinter.StringVar(value=str(settingsFromFile["notify"]) if "notify" in settingsFromFile.keys() else "True")
        notifyCheckbox = customtkinter.CTkCheckBox(leftFrame, text="", command=lambda: self.typing(None),
                                             variable=notify_check_var, onvalue="True", offvalue="False")
        notifyCheckbox.grid(row=3, column=1, pady=1, padx=5)

        ToolTip(notifyLabel, msg=Localize("NotifyCheckboxTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(notifyCheckbox, msg=Localize("NotifyCheckboxTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        tgBOTLabel = CTkLabel(leftFrame, text=Localize("ShowInTG_BOT"), font=("Arial", 17), text_color="#ffffff")
        tgBOTLabel.grid(row=4, column=0, pady=1, padx=5)

        tgBOT_check_var = customtkinter.StringVar(value=str(settingsFromFile["tgBOT"]) if "tgBOT" in settingsFromFile.keys() else "True")
        tgBOTCheckbox = customtkinter.CTkCheckBox(leftFrame, text="", command=lambda: self.typing(None),
                                             variable=tgBOT_check_var, onvalue="True", offvalue="False")
        tgBOTCheckbox.grid(row=4, column=1, pady=1, padx=5)

        ToolTip(tgBOTLabel, msg=Localize("ShowInTG_BOTTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(tgBOTCheckbox, msg=Localize("ShowInTG_BOTTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        trayCommandLabel = CTkLabel(leftFrame, text=Localize("ShowInTray"), font=("Arial", 17), text_color="#ffffff")
        trayCommandLabel.grid(row=5, column=0, pady=1, padx=5)

        trayCommand_check_var = customtkinter.StringVar(value=str(settingsFromFile["trayCommand"]) if "trayCommand" in settingsFromFile.keys() else "True")
        trayCommandCheckbox = customtkinter.CTkCheckBox(leftFrame, text="", command=lambda: self.typing(None),
                                             variable=trayCommand_check_var, onvalue="True", offvalue="False")
        trayCommandCheckbox.grid(row=5, column=1, pady=1, padx=5)

        ToolTip(trayCommandLabel, msg=Localize("ShowInTrayTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))
        ToolTip(trayCommandCheckbox, msg=Localize("ShowInTrayTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        deleteButton = customtkinter.CTkButton(leftFrame,
                                               text=Localize('delete'),
                                               fg_color=RED_COLOR,
                                               hover_color=RED_HOVER_COLOR,
                                               command=lambda: self.DeleteTask(str(urlEntry.get()).replace(" ", SPACE_SYMBOL), frame)
                                               )

        runButton = customtkinter.CTkButton(leftFrame,
                                               text=Localize('run'),
                                               command=lambda: StartTask(str(urlEntry.get()).replace(" ", SPACE_SYMBOL))
                                               )

        deleteButton.grid(row=6, column=0, pady=35, padx=5)
        deleteButton.bind("<MouseWheel>", self._on_mousewheel)

        runButton.grid(row=6, column=1, pady=35, padx=5)
        runButton.bind("<MouseWheel>", self._on_mousewheel)

        leftFrame.grid(row=0, column=0, pady=1, padx=5)

        notifyCheckbox.bind("<MouseWheel>", self._on_mousewheel)
        notifyLabel.bind("<MouseWheel>", self._on_mousewheel)
        scNumber.bind("<MouseWheel>", self._on_mousewheel)
        leftFrame.bind("<MouseWheel>", self._on_mousewheel)

        centerFrame = CTkFrame(frame, bg_color="transparent", fg_color=FOREGROUND_COLOR)

        label3 = CTkLabel(centerFrame, text=Localize("VBSScript"), font=("Arial", 17), text_color="#ffffff")
        label3.grid(row=0, column=0, pady=1, padx=5)
        ToolTip(label3, msg=Localize("VBSScriptTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11))

        self.lastNumber = number

        script = SimpleLineNumberedTextbox(centerFrame, self, width=1000, height=200)
        script.grid(row=1, column=0, pady=3, padx=5)

        if scriptText != "":
            script.insert(scriptText.rstrip())
        else:
            script.insert("""Dim WShell
Set WShell = CreateObject("WScript.Shell")

WShell.Run("notepad.exe")""")
            self.typing(self)

        script._update_line_numbers()
        script._update_comments()

        centerFrame.grid(row=0, column=1, pady=1, padx=5)

        rightFrame = CTkFrame(frame, fg_color=FOREGROUND_COLOR)

        label4 = CTkLabel(rightFrame, text=Localize("buttons"), font=("Arial", 17), text_color="#ffffff")
        label4.grid(row=0, column=0, pady=1, padx=5)
        ToolTip(label4, msg=Localize("buttonsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11), x_offset=-500)

        vb1 = settingsFromFile["button1"]
        vb2 = settingsFromFile["button2"]
        vb3 = settingsFromFile["button3"]

        opt1 = MultiColumnOptionMenu(rightFrame, options=buttons, _on_mousewheel=self._on_mousewheel, default_option=vb1, command=lambda e: self.typing(None))
        opt1.grid(row=1, column=0, padx=5, pady=5)

        labelPlus1 = CTkLabel(rightFrame, text="+", font=("Arial", 17), text_color="#ffffff")
        labelPlus1.grid(row=2, column=0, pady=1, padx=5)
        labelPlus1.bind("<MouseWheel>", self._on_mousewheel)
        ToolTip(labelPlus1, msg=Localize("buttonsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11), x_offset=-500)

        opt2 = MultiColumnOptionMenu(rightFrame, options=buttons, _on_mousewheel=self._on_mousewheel, default_option=vb2, command=lambda e: self.typing(None))
        opt2.grid(row=3, column=0, padx=5, pady=5)

        labelPlus2 = CTkLabel(rightFrame, text="+", font=("Arial", 17), text_color="#ffffff")
        labelPlus2.grid(row=4, column=0, pady=1, padx=5)
        labelPlus2.bind("<MouseWheel>", self._on_mousewheel)
        ToolTip(labelPlus2, msg=Localize("buttonsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11), x_offset=-500)

        opt3 = MultiColumnOptionMenu(rightFrame, options=buttons, _on_mousewheel=self._on_mousewheel, default_option=vb3, command=lambda e: self.typing(None))
        opt3.grid(row=5, column=0, padx=5, pady=5)

        rightFrame.grid(row=0, column=3)
        ToolTip(rightFrame, msg=Localize("buttonsTooltip"), fg="#ffffff", bg="#1c1c1c", font=("Arial", 11), x_offset=-500)

        rightFrame.bind("<MouseWheel>", self._on_mousewheel)

        URLlabel.bind("<MouseWheel>", self._on_mousewheel)
        Namelabel.bind("<MouseWheel>", self._on_mousewheel)
        label3.bind("<MouseWheel>", self._on_mousewheel)
        label4.bind("<MouseWheel>", self._on_mousewheel)

        frame.pack(side='top', anchor='center', pady=10, ipadx=5)
        frame.bind("<MouseWheel>", self._on_mousewheel)

        possibleTasksForBot[settingsFromFile["name"]] = {"urlEntry": urlEntry.get(), "tgBOT_check_var": tgBOT_check_var.get()}

        self.allTasksUI.append({"urlEntry": urlEntry, "script": script, "buttons": (opt1, opt2, opt3),
                                "deleteButton": deleteButton, "nameEntry": nameEntry,
                                "notify_check_var": notify_check_var, "tgBOT_check_var": tgBOT_check_var, "trayCommand_check_var": trayCommand_check_var})

    def _on_mousewheel(self, event):
        self.myCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.iconbitmap(default=ICON)

        self.configure(fg_color=BACKGROUND_COLOR)

        frame = customtkinter.CTkFrame(self, fg_color=FOREGROUND_COLOR)
        customtkinter.CTkButton(frame, text=Localize("settings"), command=self.open_SettingsWindow).grid(row=0, column=0, pady=10, padx=5)
        customtkinter.CTkButton(frame, text=Localize("log"), command=self.open_LogWindow).grid(row=0, column=1, pady=10, padx=5)

        CTkButton(frame, text=Localize("addTask"), command=lambda: self.AddTaskUI("", "", None, self.lastNumber + 1)).grid(row=0, column=2, pady=10, padx=5)
        self.saveButton = CTkButton(frame, text=Localize("save"), fg_color=GREEN_COLOR, hover_color=GREEN_HOVER_COLOR, command=self.Save)
        self.saveButton.grid(row=0, column=3, pady=10, padx=5)
        CTkButton(frame, text=Localize("hidetotray"), command=self.withdraw_window).grid(row=0, column=4, pady=10, padx=25)
        CTkButton(frame, text=Localize("kill") + ' ' + PROGRAM_NAME, command=self.destroy, fg_color=RED_COLOR, hover_color=RED_HOVER_COLOR).grid(row=0, column=5, pady=10, padx=30)
        frame.pack()

        #region SetWindow
        self.myCanvas = customtkinter.CTkCanvas(self, width=1515, height=1070, bd=0, bg=BACKGROUND_COLOR, highlightbackground=BACKGROUND_COLOR, highlightcolor=BACKGROUND_COLOR)
        self.frame = customtkinter.CTkFrame(self.myCanvas, width=1170, fg_color=BACKGROUND_COLOR)
        self.vsb = customtkinter.CTkScrollbar(self, command=self.myCanvas.yview, fg_color=BACKGROUND_COLOR, minimum_pixel_length=25)
        self.myCanvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y", ipadx=1, anchor="n")

        leftScroll = customtkinter.CTkCanvas(self, width=1, height=1070, bd=0, bg=BACKGROUND_COLOR, highlightbackground=BACKGROUND_COLOR, highlightcolor=BACKGROUND_COLOR)
        leftScroll.pack(side="left", fill="x", expand=True, anchor="n")

        self.myCanvas.pack(side="left", anchor="n")
        self.myCanvas.create_window((0, 0), window=self.frame, anchor="n", tags="self.frame")

        rightScroll = customtkinter.CTkCanvas(self, width=1, height=1070, bd=0, bg=BACKGROUND_COLOR, highlightbackground=BACKGROUND_COLOR, highlightcolor=BACKGROUND_COLOR)
        rightScroll.pack(side="left", fill="x", expand=True, anchor="n")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        leftScroll.bind("<MouseWheel>", self._on_mousewheel)
        rightScroll.bind("<MouseWheel>", self._on_mousewheel)
        self.myCanvas.bind("<MouseWheel>", self._on_mousewheel)
        self.frame.bind("<MouseWheel>", self._on_mousewheel)

        #endregion

        scaling_factor = get_windows_scaling()

        if scaling_factor == 1:
            self.geometry("1555x750")
        elif scaling_factor == 1.25:
            self.geometry("1255x600")
            customtkinter.set_widget_scaling(0.8)
        elif scaling_factor == 1.5:
            self.geometry("1055x500")
            customtkinter.set_widget_scaling(0.6)
        elif scaling_factor == 0.75:
            self.geometry("1755x700")
            customtkinter.set_widget_scaling(1.2)

        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)

        self.ReadSavedTasks()

        if closeToTrayOnStart == "True":
            self.withdraw_window()

        logToFile(Localize("runOn") + " " + str(PORT))

        self.mainloop()
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
    app.run(host="0.0.0.0",port=PORT)
#endregion

#region AppServerHandler

def AppServerHandler():
    global CheckWorkURL
    global AdditionalURL

    while True:
        result = ""
        try:
            if AdditionalURL == "" and CheckWorkURL == "":
                return

            if AdditionalURL != "":
                res = get(AdditionalURL, timeout=4)
                logToFile(Localize("AdditionalURLResponse") + " | " + str(res))

            if CheckWorkURL != "" and os.path.exists("RestartTunnel.vbs"):
                result = get(CheckWorkURL, timeout=4)
                result.raise_for_status()

                try:
                    if not "Ok" in result.text:
                        logToFile("RestartTunnel")
                        launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
                        sleep(10)
                    else:
                        sleep(60)
                except Exception as e:
                    logToFile("RestartTunnel")
                    launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
                    sleep(10)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            logToFile("RestartTunnel")
            launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
            sleep(10)
        except requests.exceptions.HTTPError:
            logToFile("RestartTunnel")
            launchWithoutConsole(["cmd", "/c", "RestartTunnel.vbs"])
            sleep(10)
        except Exception as e:
            logToFile("get error: " + str(e))
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
        Notify(Localize("NotifyOnStartMessage"))

    AppWindow()
