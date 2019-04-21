from discord import *

from .BaseHandler import BaseHandler
from util import *
import database


class Language(BaseHandler):
    async def list(self, info):
        em = Embed(title="Language List", description="List of available languages", color=BOT_COLOUR)
        em.add_field(name="Languages", value="\n".join(judge_lang.keys()))
        await info['bot'].send_message(info['channel'], embed=em)

    async def current(self, info):
        await info['bot'].send_message(info['channel'], "Your current language is `{}`".format(info['user'].language))

    async def change(self, info):
        try:
            lang = info['content'][0]
            if lang not in judge_lang.keys():
                raise IndexError
            with await database.locks["user"][info['user'].id]:
                info['user'].language = lang
                await info['bot'].send_message(info['channel'], "Your language has been changed to `{}`".format(lang))
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid language.")
