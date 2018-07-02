from .BaseHandler import BaseHandler
from .Problem import Problem
from discord import *
from util import *
import database
import models
import os

class Contest(BaseHandler):
    async def list(self, info):
        current_list, page_num = await get_current_list(info, list(database.contest_list.values()))
        if current_list is None:
            return
        em = Embed(title="Contests",description="Contest page {}".format(page_num), color=BOT_COLOUR)
        for x in current_list:
            em.add_field(name=x.name, value="\n".join(y.problem_name for y in x.problems))
        await info['bot'].send_message(info['channel'], embed=em)
    
    async def add(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "add contests"):
            return
        content = info['content']
        try:
            contest_name = content[0]
            if contest_name in database.contest_list.keys():
                raise ValueError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a contest name.");
            return
        except ValueError:
            await info['bot'].send_message(info['channel'], "Contest with name `{}` already exists.".format(contest_name))
            return
        for x in content[1:]:
            if x not in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "Problem `{}` does not exist. The contest cannot be created.".format(x))
                return
        if len(content) == 1:
            await info['bot'].send_message(info['channel'], "Cannot create an empty contest!")
        elif len(content[1:]) != len(set(content[1:])):
            await info['bot'].send_message(info['channel'], "Cannot create contest with duplicate problems.")
        elif len(content) > 8:
            await info['bot'].send_message(info['channel'], "Cannot create a contest with more than 8 problems.")
        else:
            database.contest_list[contest_name] = models.Contest(contest_name, [database.problem_list[x] for x in content[1:]])
            await info['bot'].send_message(info['channel'], "Contest `{}` successfully created!".format(contest_name))

    async def delete(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "delete contests"):
            return
        content = info['content']
        try:
            contest_name = content[0]
            if contest_name not in database.contest_list.keys():
                raise ValueError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a contest name.")
            return
        except ValueError:
            await info['bot'].send_message(info['channel'], "Contest `{}` does not exist.".format(contest_name))
            return
        del database.contest_list[contest_name]
        try:
            os.remove("contests/{}.json".format(contest_name))
        except FileNotFoundError:
            pass
        await info['bot'].send_message(info['channel'], "Contest `{}` sucessfully deleted.".format(contest_name))

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
                await info['game'].start_round(c, info['user'], time_limit)
            except (IndexError, ValueError):
                await info['game'].start_round(c, info['user'])

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
        await Problem().submit(info, contest=info['game'])

    async def problem(self, info):
        await info['game'].display_problem(info['user'], info['content'][0].strip().lower() if len(info['content']) > 0 else " ")
