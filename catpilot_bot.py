# Телеграм-бот: список задач кнопками, запуск задачи по названию или URL, открытие ссылок
import subprocess
import threading
from contextlib import suppress

import telebot
from telebot import types

from catpilot_config import IsOn, Setting
from catpilot_instance import AddShutdownHandler
from catpilot_localization import Localize
from catpilot_log import LogToFile
from catpilot_notify import Notify
import catpilot_tasks
from catpilot_tasks import FindTask, StartTask

# Список открывается и по части строки ("help", "start", "команды"), а не только по точной команде
COMMANDS_TO_START_BOT = "/start /help /commands /начать /помощь /команды"
LINK_MARKERS = ("http", ".ru", ".com")
OPEN_LINK_SCRIPT = "OpenBrowserLink.vbs"
# Через сколько секунд удаляется сообщение со списком команд
COMMANDS_MESSAGE_LIFETIME = 30

bot = None
allowedIds = set()

def IsAllowed(user):
    return user is not None and str(user.id) in allowedIds

def DeleteMessageLater(chatId, messageId):
    def delete():
        with suppress(Exception):
            bot.delete_message(chatId, messageId)

    threading.Timer(COMMANDS_MESSAGE_LIFETIME, delete).start()

def SendCommands(chatId):
    markup = types.InlineKeyboardMarkup()

    for task in catpilot_tasks.loadedTasks:
        if task["tgBOT"] == "True":
            # В callback_data влезает только 64 байта, поэтому передаём URL, а не название
            markup.add(types.InlineKeyboardButton(task["name"], callback_data=task["url"]))

    LogToFile("TG BOT: " + Localize("Commands"))
    message = bot.send_message(chatId, text=Localize("Commands"), reply_markup=markup)
    DeleteMessageLater(chatId, message.id)

def OpenLink(chatId, link):
    link = link.strip().replace(" ", "%20")
    # wscript без cmd: в ссылке бывают &, ^, | — для cmd это спецсимволы
    subprocess.Popen(["wscript.exe", OPEN_LINK_SCRIPT, link])
    bot.send_message(chatId, text=Localize("Open"))
    LogToFile("TG BOT: " + Localize("Open") + " | " + link)
    if IsOn("showNotifications"):
        Notify(Localize("Open") + " | " + link)

def RunTaskFromTG(nameOrUrl, chatId):
    task = FindTask(nameOrUrl)
    if task is None:
        bot.send_message(chatId, text=nameOrUrl + " | " + Localize("fail"))
        return

    StartTask(task["url"])
    bot.send_message(chatId, text=Localize("CarryOut"))

def RejectUser(chatId):
    LogToFile("TG BOT: " + Localize("NotAllowed"))
    bot.send_message(chatId, text=Localize("NotAllowed"))

def OnCallback(callback):
    with suppress(Exception):
        bot.answer_callback_query(callback.id)

    if callback.message is None:
        return

    chatId = callback.message.chat.id
    if not IsAllowed(callback.from_user):
        RejectUser(chatId)
        return

    RunTaskFromTG(str(callback.data), chatId)

def OnMessage(message):
    chatId = message.chat.id

    if not IsAllowed(message.from_user):
        RejectUser(chatId)
        return

    text = (message.text or "").strip()
    if text == "":
        return

    if text.lower() in COMMANDS_TO_START_BOT:
        SendCommands(chatId)
    elif any(marker in text for marker in LINK_MARKERS):
        OpenLink(chatId, text)
    else:
        RunTaskFromTG(text, chatId)

def StopBot():
    if bot is not None:
        with suppress(Exception):
            bot.stop_polling()

def RunBot():
    global bot

    token = Setting("TG_TOKEN")
    if token == "":
        return

    allowedIds.update(id.strip() for id in Setting("AllowedTG_IDs").split(",") if id.strip())

    bot = telebot.TeleBot(token)
    bot.register_callback_query_handler(OnCallback, func=lambda callback: True)
    bot.register_message_handler(OnMessage, func=lambda message: True)
    AddShutdownHandler(StopBot)

    # infinity_polling сам переподключается после ошибок сети
    bot.infinity_polling(timeout=20, long_polling_timeout=20)

def StartBot():
    threading.Thread(target=RunBot, name="Bot", daemon=True).start()
