import os

import botlab
import telebot

import settings

__author__ = 'Xomak'

always_spare_laundry = 43
global_memory = {"status": {42: [True, True, True], always_spare_laundry: [True, True, True]}}

if settings.SETTINGS['bot']['token'] is None:
    token = os.environ.get('BOT_TOKEN')
    settings.SETTINGS['bot']['token'] = token

bot = botlab.BotLab(settings.SETTINGS)


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

    return kb


@bot.message_handler(state='main_menu')
def main_menu_state(session, message):
    text = message.text

    if text == session._("btn_free_equipment"):
        # TODO: Add proper keyboard here
        session.set_state("free_equipment_main")
        session.reply_message(session._("msg_request_laundry_id"))
    else:
        session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


@bot.message_handler(state='free_equipment_main')
def free_equipment_laundry_id_state(session, message):
    laundry_id = int(message.text)
    session.set_state("free_equipment_actions")

    reply_msg = session._("msg_avail_equipment") + "\n\n"

    reply_msg += get_machines_list_str(session, laundry_id)

    session.reply_message(reply_msg, reply_markup=build_free_equipment_notify_keybord(session))


@bot.message_handler(state='free_equipment_actions')
def free_equipment_actions_state(session, message):
    text = message.text

    session.set_state("main_menu")

    if text == session._("btn_notify_on_release_machine") or \
        text == session._("btn_notify_on_release_machine"):
        session.reply_message(session._("msg_notify_on_release"), reply_markup=build_main_menu_keyboard(session))
    else:
        reply_msg = session._("msg_avail_equipment") + "\n\n"
        reply_msg += get_machines_list_str(session, always_spare_laundry)

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

bot.polling(timeout=1)
