from discord import *
from util import *
import asyncio
import database

lock = asyncio.Lock()

class Contest:
    @staticmethod
    async def help(info):
        em = Embed(title="Contest Help",description="Available Contest commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list["contest"].items():
            em.add_field(name=COMMAND_PREFIX + "contest " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        em = Embed(title="Contest List", description="List of available contests.", color=BOT_COLOUR)
        for x in database.contest_list.values():
            em.add_field(name=x.name, value="\n".join(y.problem_name for y in x.problems))
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def start(info):
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

    @staticmethod
    async def join(info):
        await info['game'].join(info['user'])

    @staticmethod
    async def rankings(info):
        await info['game'].rankings()

    @staticmethod
    async def info(info):
        await info['game'].info()

    @staticmethod
    async def end(info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "forcefully end contests"):
            return
        await info['game'].end_round()

    @staticmethod
    async def submit(info):
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


    @staticmethod
    async def problem(info):
        await info['game'].display_problem(info['user'], info['content'][0].strip().lower() if len(info['content']) > 0 else " ")
