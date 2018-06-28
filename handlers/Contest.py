from .BaseHandler import BaseHandler
from discord import *
from util import *
import asyncio
import database

lock = asyncio.Lock()

class Contest(BaseHandler):
    async def list(self, info):
        current_list, page_num = await get_current_list(info, list(database.contest_list.values()))
        if current_list is None:
            return
        em = Embed(title="Contests",description="Contest page {}".format(page_num), color=BOT_COLOUR)
        for x in current_list:
            em.add_field(name=x.name, value="\n".join(y.problem_name for y in x.problems))
        await info['bot'].send_message(info['channel'], embed=em)

    async def start(self, info):
        if len(info['content']) < 1:
            await info['bot'].send_message(info['channel'], "Please select a contest to run.")
        else:
            try:
                c = database.contest_list[info['content'][0].lower()]
            except KeyError:
                await info['bot'].send_message(info['channel'], "Please enter a valid contest.")
                return
            try:
                time_limit = int(info['content'][1])
                if time_limit < 1 or time_limit > 31536000:
                    raise ValueError
                await info['game'].start_round(c, time_limit)
            except (IndexError, ValueError):
                await info['game'].start_round(c)

    async def join(self, info):
        await info['game'].join(info['user'])

    async def rankings(self, info):
        await info['game'].rankings()

    async def info(self, info):
        await info['game'].info()

    async def end(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "forcefully end contests"):
            return
        await info['game'].end_round()

    async def submit(self, info):
        global lock
        if len(info['message'].attachments) != 1:
            await info['bot'].send_message(info['channel'], "Please upload one file for judging.")
        elif len(info['content']) != 1:
            await info['bot'].send_message(info['channel'], "Please select a problem to submit the code to.")
        else:
            with await lock:
                this_id = database.id
                database.id += 1
            await info['game'].submit(info['message'], info['user'], info['content'][0], info['message'].attachments[0]["url"], this_id)

    async def problem(self, info):
        await info['game'].display_problem(info['user'], info['content'][0].strip().lower() if len(info['content']) > 0 else " ")
