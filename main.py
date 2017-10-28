import os

import botlab
import settings

__author__ = 'Xomak'


if settings.SETTINGS['bot']['token'] is None:
    settings.SETTINGS['bot']['token'] = os.environ.get('BOT_TOKEN')

bot = botlab.BotLab(settings.SETTINGS)


@bot.message_handler(state='main_menu')
def main_menu_state(session, message):

    session.reply_message("Quaia quaia coronoid!")


bot.polling(timeout=1)
