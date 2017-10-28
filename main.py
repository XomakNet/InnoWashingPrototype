import os

import botlab
import telebot

import settings

__author__ = 'Xomak'


if settings.SETTINGS['bot']['token'] is None:
    settings.SETTINGS['bot']['token'] = os.environ.get('BOT_TOKEN')

bot = botlab.BotLab(settings.SETTINGS)


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


bot.polling(timeout=1)
