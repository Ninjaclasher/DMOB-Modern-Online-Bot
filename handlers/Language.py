from discord import *
from util import *
import database

class Language:
    @staticmethod
    async def help(info):
        em = Embed(title="Language Help",description="Available Language commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list["language"].items():
            em.add_field(name=COMMAND_PREFIX + "language " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        em = Embed(title="Language List", description="List of available languages", color=BOT_COLOUR)
        em.add_field(name="Languages", value="\n".join(judge_lang.keys()))
        await info['bot'].send_message(info['channel'], embed=em)
    
    @staticmethod
    async def current(info):
        await info['bot'].send_message(info['channel'], "Your current language is `" + info['user'].language + "`")

    @staticmethod
    async def change(info):
        try:
            lang = info['content'][0]
            if lang not in judge_lang.keys():
                raise IndexError
            info['user'].language = lang
            await info['bot'].send_message(info['channel'], "Your language has been changed to `" + lang + '`')
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid language.")
