__author__ = 'Xomak'

SETTINGS = {
    'config': {
        'sync_strategy': 'hot', # 'hot' or 'cold'
        # hot - sync all the changes made to bot configuration
        #   (including l10n) during runtime with kv-storage so
        #   that they are available after bot restarted.
    },
    'bot': {
        'token': None,
        # The states new bot users will fall into once
        #   they started the bot.
        'initial_state': 'main_menu',
        'initial_inline_state': None,
        # If the flag is up, exceptions from telegram server
        #   (when using methods like `edit_message_text` and etc.)
        #   won't be propagated and raised. It is useful to have this
        #   option ON since it helps to prevent bot from going down in
        #   production because of errors like `bot was blocked by the user`
        #   and stuff.
        # You don't need to dirt your code with a bunch of try..except
        #   blocks for every single api call you make if this option is ON.
        'suppress_exceptions': True
    },
    'db_storage': {
        'type': 'disk',
        'params': {
            'file_path': 'data/storage.json'
        }
    },
    'kv_storage': {
        'type': 'inmemory',
        'params': {}
    },
    'l10n': {
        # The language that is set to the user by default
        'default_lang': 'en',
        # Path to the file with l10n
        'file_path': 'locale/default.json'
    }
}