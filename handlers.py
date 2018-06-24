from discord import *
from models import Submission
from util import *
import asyncio
import database

lock = asyncio.Lock()

class Contests:
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

class Submissions:
    @staticmethod
    async def help(info):
        em = Embed(title="Submissions Help",description="Available Submissions commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list["submissions"].items():
            em.add_field(name=COMMAND_PREFIX + "submissions " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        try:
            page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
            elements_per_page = 9
            if page_num < 1 or (page_num-1)*elements_per_page > len(database.submission_list):
                raise ValueError
            em = Embed(title="Submissions",description="Submission page " + str(page_num), color=BOT_COLOUR)
            for x in range((page_num-1)*elements_per_page, min(page_num*elements_per_page, len(database.submission_list))):
                cur = database.submission_list[x]
                values = ["By: " + str(cur.user.discord_user), "Problem: " + str(cur.problem.problem_name), "Score: " + str(cur.points) + "/" + str(cur.total), "Verdict: " + cur.result + " (" + verdicts[cur.result] + ")"]
                em.add_field(name="Submission #" + str(cur.submission_id), value='\n'.join(values))
            await info['bot'].send_message(info['channel'], embed=em)
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Please enter a valid page number.")

    @staticmethod
    async def view(info):
        try:
            sub = get_element(database.submission_list, Submission(int(info['content'][0])))
            if sub is None:
                raise KeyError
        except (ValueError, KeyError):
            await info['bot'].send_message(info['channel'], "Please enter a valid submission id.")
            return
        try:
            em = Embed(title="Submission Details", description=info['description'], color=BOT_COLOUR)
        except KeyError:
            em = Embed(title="Submission Details", description="Details on submission #" + info['content'][0], color=BOT_COLOUR)
        em.add_field(name="Problem Name", value=sub.problem.problem_name)
        em.add_field(name="Submission ID", value=str(sub.submission_id))
        em.add_field(name="Verdict", value=sub.result + " (" + verdicts[sub.result] + ")")
        em.add_field(name="Points Recieved", value=str(sub.points) + "/" + str(float(sub.total)))
        em.add_field(name="Total Running Time", value=str(round(sub.time,2)) + "s")
        em.add_field(name="Memory Usage", value=to_memory(sub.memory))
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def code(info):
        try:
            sub = get_element(database.submission_list, Submission(int(info['content'][0])))
            if sub is None:
                raise KeyError
        except (ValueError, KeyError):
            await info['bot'].send_message(info['channel'], "Please enter a valid submission id.")
            return
        if not sub.is_by(info['user']) and not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], info['user'].discord_user.mention, " You do not have permission to view submission #" + str(sub.submission_id))
            return
        await info['bot'].send_message(info['user'].discord_user, "Code preview:\n```\n" + sub.source[:1900] + "\n```\n")
        await info['bot'].send_file(info['user'].discord_user, "submissions/" + str(sub.submission_id) + ".code")
        await info['bot'].send_message(info['channel'], info['user'].discord_user.mention + " The code has been sent to your private messages.")

    @staticmethod
    async def delete(info):
        try:
            sub = get_element(database.submission_list, Submission(int(info['content'][0])))
            if sub is None:
                raise KeyError
        except (ValueError, KeyError):
            await info['bot'].send_message(info['channel'], "Please enter a valid submission id.")
            return
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to delete submission #" + str(sub.submission_id))
            return
        database.submission_list.remove(sub)
        os.system("mv submissions/" + str(sub.submission_id) + ".* deleted_submissions/")
        await info['bot'].send_message(info['channel'], "Successfully deleted submission #" + str(sub.submission_id))

