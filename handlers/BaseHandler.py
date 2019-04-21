from discord import *
from util import *


class BaseHandler:
    async def help(self, info):
        name = self.__class__.__name__
        em = Embed(title="{} Help".format(name), description="Available {} commands from DMOB".format(name), color=BOT_COLOUR)
        for key, value in help_list[name.lower()].items():
            em.add_field(name="{}{} {}".format(COMMAND_PREFIX, name.lower(), key), value=value)
        await info['bot'].send_message(info['channel'], embed=em)
