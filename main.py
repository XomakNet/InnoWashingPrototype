import os

import botlab
import telebot

import settings

__author__ = 'Xomak'


if settings.SETTINGS['bot']['token'] is None:
    settings.SETTINGS['bot']['token'] = os.environ.get('BOT_TOKEN')

bot = botlab.BotLab(settings.SETTINGS)


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
    else:
        session.reply_message(session._("msg_main_menu"), reply_markup=build_main_menu_keyboard(session))


bot.polling(timeout=1)
