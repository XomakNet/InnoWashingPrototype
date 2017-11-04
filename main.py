import os
import threading

import botlab
import telebot
from flask import Flask


import settings

__author__ = 'Xomak'

global_memory = {"status": {42: [True, True, True, True]}}

if settings.SETTINGS['bot']['token'] is None:
    token = os.environ.get('BOT_TOKEN')
    settings.SETTINGS['bot']['token'] = token

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

    kb.add(telebot.types.KeyboardButton(text=session._("btn_current_reminders")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_cancel")))

    return kb


def build_main_menu_keyboard(session):
    kb = telebot.types.ReplyKeyboardMarkup(row_width=1)

    kb.add(telebot.types.KeyboardButton(text=session._("btn_free_equipment")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_notify_me")))

    return kb


def build_free_equipment_notify_keybord(session):
    kb = telebot.types.ReplyKeyboardMarkup(row_width=1)

    kb.add(telebot.types.KeyboardButton(text=session._("btn_notify_on_release_machine")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_nearest_machine")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_notify_on_release_drier")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_nearest_drier")))
    kb.add(telebot.types.KeyboardButton(text=session._("btn_cancel")))

    return kb


@bot.message_handler(state='main_menu')
def main_menu_state(session, message):
    text = message.text

    if text == session._("btn_free_equipment"):
        session.set_state("free_equipment_main")
        session.reply_message(session._("msg_request_laundry_id"))
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
    session.set_state("main_menu")
    session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


@bot.message_handler(state='free_equipment_main')
def free_equipment_main_state(session, message):
    if message.text.isdigit():
        laundry_id = int(message.text)

        if laundry_id in global_memory["status"]:
            session.set_state("free_equipment_actions")

            reply_msg = session._("msg_avail_equipment") + "\n\n"

            reply_msg += get_machines_list_str(session, laundry_id)

            session.reply_message(reply_msg, reply_markup=build_free_equipment_notify_keybord(session))
        else:
            session.set_state('free_equipment_main')
            session.reply_message(session._("msg_unexpected_laundry_id"))
    else:
        session.set_state('free_equipment_main')
        session.reply_message(session._("msg_id_number_error"))




@bot.message_handler(state='subscribe_on_laundry')
def subscribe_on_laundry_state(session, message):
    text = message.text
    if text == session._("btn_yes"):
        session.reply_message(session._("msg_reserved"))
    else:
        session.reply_message(session._("msg_notify_on_release"))
    session.set_state("main_menu")
    session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


@bot.message_handler(state='free_equipment_actions')
def free_equipment_actions_state(session, message):
    if message.text == session._("btn_cancel"):
        session.set_state("main_menu")
        session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))
    else:
        text = message.text

        session.set_state("main_menu")

        if text == session._("btn_notify_on_release_machine") or \
                        text == session._("btn_notify_on_release_drier"):
            session.set_state("subscribe_on_laundry")
            kb = telebot.types.ReplyKeyboardMarkup(row_width=1)
            kb.add(telebot.types.KeyboardButton(text=session._("btn_yes")))
            kb.add(telebot.types.KeyboardButton(text=session._("btn_no")))
            session.reply_message(session._("msg_ask_for_reserve"), reply_markup=kb)

        elif text == session._("btn_nearest_machine"):
            reply_msg = session._("msg_avail_equipment") + "\n\n"
            reply_msg += "431" + " " + session._("type_washing_machine") + " - " + session._("status_free") + "\n\n"
            reply_msg += "432" + " " + session._("type_washing_machine") + " - " + session._("status_free") + "\n\n"
            reply_msg += "441" + " " + session._("type_washing_machine") + " - " + session._("status_free") + "\n\n"
            reply_msg += "442" + " " + session._("type_washing_machine") + " - " + session._("status_free") + "\n\n"

            session.reply_message(reply_msg, reply_markup=build_main_menu_keyboard(session))
        elif text == session._("btn_nearest_drier"):
            reply_msg = session._("msg_avail_equipment") + "\n\n"
            reply_msg += "433" + " " + session._("type_drier") + " - " + session._("status_free") + "\n\n"
            reply_msg += "434" + " " + session._("type_drier") + " - " + session._("status_free") + "\n\n"
            reply_msg += "443" + " " + session._("type_drier") + " - " + session._("status_free") + "\n\n"
            reply_msg += "444" + " " + session._("type_drier") + " - " + session._("status_free") + "\n\n"

            session.reply_message(reply_msg, reply_markup=build_main_menu_keyboard(session))


def get_machines_list_str(session, laundry_id):
    list_str = ""
    equipment_list = global_memory["status"][laundry_id]

    for i in range(0, len(equipment_list)):
        machine_type = get_machine_type_str(i)
        if equipment_list[i]:
            list_str += str(laundry_id) + str(i + 1) + " " + session._(machine_type) + " - " +\
                        session._("status_occupied") + "\n\n"
        else:
            list_str += str(laundry_id) + str(i + 1) + " " + session._(machine_type) + " - " +\
                        session._("status_free") + "\n\n"

    return list_str


def get_machine_type_str(index):
    if index < 2:
        return "type_washing_machine"
    else:
        return "type_drier"

def flask_run():
    app.run()

#app.run()
t1 = threading.Thread(target=flask_run)
t1.start()

bot.polling(timeout=1)
t1.join()