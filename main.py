import os
import threading

import botlab
import telebot
from flask import Flask


import settings

__author__ = 'Xomak'


if settings.SETTINGS['bot']['token'] is None:
    settings.SETTINGS['bot']['token'] = os.environ.get('BOT_TOKEN')

bot = botlab.BotLab(settings.SETTINGS)

app = Flask(__name__)


@app.route("/notify_my")
def notify_my():
    bot.broadcast_message({'lang': 'en'}, 'Washing machine 421 has finished.')
    return "Ok"


@app.route("/notify_others")
def notify_others():
    bot.broadcast_message({'lang': 'en'}, 'Washing machine in laundry 42 has finished, hurry up!')
    return "Ok"


@app.route("/notify_others_reserved")
def notify_others_reserved():
    kb = telebot.types.ReplyKeyboardMarkup(row_width=1)
    kb.add(telebot.types.KeyboardButton(text="Unlock"))
    kb.add(telebot.types.KeyboardButton(text="I changed my mind. Release it."))
    bot.broadcast_message({'lang': 'en'}, "Washing machine 422 in laundry 42 has finished, it is locked and is waiting "
                                          "for you. \nPress \"unlock\" button, when you are ready.", reply_markup=kb)

    sessions = bot._storage.get_object(botlab.Session.SESSIONS_COLLECTION, {"lang": "en"}, multi=True)
    for session in sessions:
        bot._get_session(session['chat_id']).set_state("ready_to_wash")

    return "Ok"


def build_notify_me_keyboard(session):
    kb = telebot.types.ReplyKeyboardMarkup(row_width=1)

    kb.add(telebot.types.KeyboardButton(text=session._("btn_cancel")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_current_reminders")))

    return kb


def build_main_menu_keyboard(session):
    kb = telebot.types.ReplyKeyboardMarkup(row_width=1)

    kb.add(telebot.types.KeyboardButton(text=session._("btn_free_equipment")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_notify_me")))

    return kb


@bot.message_handler(state='main_menu')
def main_menu_state(session, message):
    text = message.text

    if text == session._("btn_free_equipment"):
        # TODO: Add proper keyboard here
        session.set_state("free_equipment_main")
        session.reply_message(session._("msg_free_equipment_main"))
    elif text == session._("btn_notify_me"):
        session.set_state("notify_me")
        session.reply_message(session._("msg_notify_me"), reply_markup=build_notify_me_keyboard(session))
    else:
        session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


@bot.message_handler(state='notify_me')
def notify_me_state(session, message):
    session.set_state("main_menu")

    if message.text == session._("btn_current_reminders"):
        kb = telebot.types.ReplyKeyboardMarkup(row_width=1)
        kb.add(telebot.types.KeyboardButton(text="Washing machine 421"))
        kb.add(telebot.types.KeyboardButton(text=session._("btn_cancel")))
        session.reply_message("Press on notification to remove it.", reply_markup=kb)
    else:
        if message.text.isdigit():
            session.reply_message(session._("msg_notification_created"))
        session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


@bot.message_handler(state='ready_to_wash')
def ready_to_wash_state(session, message):
    if message.text != "I changed my mind. Release it.":
        session.reply_message(session._("msg_washing_started"))
    else:
        session.reply_message("Okay.")
    session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


def flask_run():
    app.run()

#app.run()
t1 = threading.Thread(target=flask_run)
t1.start()
bot.polling(timeout=1)
t1.join()

