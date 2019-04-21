from .BaseHandler import BaseHandler
from .Problem import Problem
from discord import *
from util import *
import database
import models


def get_contest(contest_name):
    try:
        return database.get_contests(name=contest_name)[0]
    except IndexError:
        return None


class Contest(BaseHandler):
    async def list(self, info):
        current_list, page_num = await get_current_list(info, database.get_contests())
        if current_list is None:
            return
        em = Embed(title="Contests", description="Contest page {}".format(page_num), color=BOT_COLOUR)
        if len(current_list) == 0:
            em.add_field(name="No Contests", value="There are no contests.")
        else:
            for x in current_list:
                em.add_field(name=x.name, value="\n".join(y.name for y in x.problems))
        await info['bot'].send_message(info['channel'], embed=em)

    async def add(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "add contests"):
            return
        content = info['content']
        try:
            contest_name = content[0]
            if get_contest(contest_name) is not None:
                raise ValueError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a contest name.")
            return
        except ValueError:
            await info['bot'].send_message(info['channel'], "Contest with name `{}` already exists.".format(contest_name))
            return
        s = set(content[1:])
        not_exist = s - set(database.problem_list.keys())
        if len(not_exist) > 0:
            await info['bot'].send_message(info['channel'], "The following problems do not exist, so the contest cannot be created: `{}`".format(" ".join(not_exist)))
            return
        elif len(content) == 1:
            await info['bot'].send_message(info['channel'], "Cannot create an empty contest!")
        elif len(content[1:]) != len(s):
            await info['bot'].send_message(info['channel'], "Cannot create contest with duplicate problems.")
        elif len(content) > 8:
            await info['bot'].send_message(info['channel'], "Cannot create a contest with more than 8 problems.")
        else:
            database.add_contest(models.Contest(None, contest_name, content[1:]))
            await info['bot'].send_message(info['channel'], "Contest `{}` successfully created!".format(contest_name))

    async def delete(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "delete contests"):
            return
        content = info['content']
        try:
            contest_name = content[0]
            contest = get_contest(contest_name)
            if contest is None:
                raise ValueError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a contest name.")
            return
        except ValueError:
            await info['bot'].send_message(info['channel'], "Contest `{}` does not exist.".format(contest_name))
            return
        database.delete_contest(contest)

        await info['bot'].send_message(info['channel'], "Contest `{}` sucessfully deleted.".format(contest_name))

    async def start(self, info):
        if info['game'] is not None and not info['game'].contest_over:
            await info['bot'].send_message(info['channel'], "There is already a contest runnning in this channel. Please wait until the contest is over.")
            return
        try:
            contest_name = info['content'][0]
            contest = get_contest(contest_name)
            if contest is None:
                raise KeyError
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please select a contest to run.")
            return
        except KeyError:
            await info['bot'].send_message(info['channel'], "Please enter a valid contest.")
            return
        try:
            time_limit = int(info['content'][1])
            if time_limit < 1 or time_limit > 31536000:
                raise ValueError
        except (IndexError, ValueError):
            time_limit = 10800

        import DMOBGame
        channel_id = info['channel'].id
        game = DMOBGame.DMOBGame(info['bot'], None, channel_id, contest=contest.id, window=time_limit)
        game.id = database.create_game(game)
        database.games[channel_id] = game
        await game.start_round(info['user'])

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
