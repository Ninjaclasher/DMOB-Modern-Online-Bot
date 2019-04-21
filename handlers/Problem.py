import asyncio
import datetime
import requests

from .BaseHandler import BaseHandler
from discord import *
from util import *

import database
import handlers
import models


async def wait_submission_finish(bot, channel, id, user, contest):
    if contest is not None:
        await contest.on_start_submission(id)
    while True:
        try:
            sub = database.judgeserver.judges.finished_submissions[id]
            with await database.locks["submissions"][id]:
                database.add_submission(sub)
                sub = database.get_submissions(id=id, contest_subs=True)[0]
                await sub.user.update_points()
                if contest is not None:
                    await contest.on_finish_submission(sub)
            print(sub)
            info = {
                'bot': bot,
                'channel': channel if contest is None else user.discord_user,
                'user': user,
                'content': [str(id)],
            }
            await handlers.Submissions().view(info, live_submission=True, submission=sub)
            return
        except KeyError:
            pass
        await asyncio.sleep(0.5)


class Problem(BaseHandler):
    command_help = {}
    command_help["add"] = [
        ["Command", "`" + COMMAND_PREFIX + "problem add (problem code) (problem name) (point value) (time limit) (memory limit)`"],
        ["Details", "Please include a file when adding the problem as the problem statement."],
        ["problem code", "The problem code that the problem should have. This should be unique with all problems."],
        ["problem name", "The user readable problem name."],
        ["point value", "An integer value for the point value of the problem."],
        ["time limit", "An integer value for the time limit (in seconds) of the problem."],
        ["memory limit", "An integer value for the memory limit (in kilobytes) of the problem."],
    ]
    command_help["change"] = [
        ["Command", "`" + COMMAND_PREFIX + "problem change (problem code) (field to change) (new value)`"],
        ["problem code", "The problem code for the problem to change."],
        ["field to change", "The field in the problem to change. Possible fields are: [`" + "`, `".join(set(models.Problem().__dict__.keys()) - unchangeable_problem_fields) + "`]"],
        ["new value", "The new value for the field specified."],
    ]

    async def list(self, info):
        current_list, page_num = await get_current_list(info, list(database.problem_list.values()), 35)
        current_list.sort(key=lambda x: x.name)
        if current_list is None:
            return
        em = Embed(title="Problems", description="Problem page {}".format(page_num), color=BOT_COLOUR)
        em.add_field(name="Problem Name", value='\n'.join(x.name for x in current_list))
        em.add_field(name="Problem Code", value='\n'.join(x.code for x in current_list))
        em.add_field(name="Is Public", value='\n'.join("Y" if x.is_public else "N" for x in current_list))
        await info['bot'].send_message(info['channel'], embed=em)

    async def view(self, info, in_contest=False):
        try:
            problem_code = info['content'][0].lower()
            problem = database.problem_list[problem_code]
        except KeyError:
            await info['bot'].send_message(info['channel'], "Please enter a valid problem code.")
            return
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a problem code.")
            return
        with await database.locks["problem"][problem_code]:
            if not await has_perm(info['bot'], info['channel'], info['user'], "view this problem", not problem.is_public and not in_contest):
                return
            description = "Details on problem `{}`".format(problem.code) if not in_contest else info['description']
            em = Embed(title="Problem Info", description=description, color=BOT_COLOUR)
            em.add_field(name="Problem Name", value=problem.name)
            em.add_field(name="Problem Code", value=problem.code)
            em.add_field(name="Point Value", value="{}p".format(problem.point_value if not in_contest else 100))
            em.add_field(name="Time Limit", value="{}s".format(problem.time_limit))
            em.add_field(name="Memory Limit", value=to_memory(problem.memory_limit))
            if not in_contest and info['user'].is_admin:
                em.add_field(name="Is Public", value="Y" if problem.is_public else "N")

        await info['bot'].send_message(info['user'].discord_user, embed=em)
        await info['bot'].send_file(info['user'].discord_user, problem.file)
        await info['bot'].send_message(info['channel'], "{}, problem statement has been sent to your private messages.".format(info['user'].discord_user.mention))

    async def add(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "add problems"):
            return
        content = info['content']
        if len(content) == 1 and content[0].lower() == "help":
            em = Embed(title="Problem Adding Help", description="Details on how to add a problem.", color=BOT_COLOUR)
            for x in Problem.command_help["add"]:
                em.add_field(name=x[0], value=x[1])
            await info['bot'].send_message(info['channel'], embed=em)
            return

        try:
            if len(info['message'].attachments) != 1:
                await info['bot'].send_message(info['channel'], "Please upload one file for the problem statement.")
                return
            elif len(content) < 5:
                raise IndexError
            problem_code = content[0].lower()
            name = " ".join(content[1:-3])
            point_value, time_limit, memory_limit = map(int, content[-3:])
        except (KeyError, ValueError, IndexError, requests.HTTPError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to create a new problem. Please try again.")

        with await database.locks["problem"][problem_code]:
            if problem_code in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "A problem with problem code `{}` already exists. Please try again.".format(problem_code))
                return
            id = database.add_problem(models.Problem(None, name, problem_code, info['user'].id, time_limit, memory_limit, point_value))
            with open("problems/{0}.pdf".format(id), "wb") as f:
                f.write(requests.get(info['message'].attachments[0]['url']).content)
        await info['bot'].delete_message(info['message'])
        await info['bot'].send_message(info['channel'], "Problem `{}` successfully created!".format(problem_code))

    async def change(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "change problems"):
            return
        content = info['content']
        if len(content) == 1 and content[0].lower() == "help":
            em = Embed(title="Problem Changing Help", description="Details on how to change a problem.", color=BOT_COLOUR)
            for x in self.command_help["change"]:
                em.add_field(name=x[0], value=x[1])
            await info['bot'].send_message(info['channel'], embed=em)
            return

        exceptions = {
            KeyError: "The problem that you entered does not exist.",
            IndexError: "Failed to parse the message content to change the problem. Please try again.",
            ValueError: "The specified new value is invalid. Please try again.",
            TypeError: "Cannot change the field you entered. Please try again.",
        }
        try:
            problem_code = content[0].lower()
            field = content[1].lower()
            value = content[2]
            if field != "name":
                value = int(value)
            problem = database.problem_list[problem_code]
            if field in unchangeable_problem_fields or field not in problem.__dict__.keys():
                raise TypeError
        except (*exceptions,) as e:
            await info['bot'].send_message(info['channel'], exceptions[type(e)])
            return
        with await database.locks["problem"][problem_code]:
            database.change_problem(problem, field, value)
        await info['bot'].send_message(info['channel'], "Successfully changed problem `{}`.".format(problem_code))

    async def make(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "change a problem's visibility"):
            return

        exceptions = {
            KeyError: "The problem that you entered does not exist.",
            IndexError: "Failed to parse the message content to change the problem. Please try again.",
            ValueError: "The specified new value is invalid. Please enter `public` or `private` try again.",
        }
        try:
            value = info['content'][0].lower()
            problem_code = info['content'][1].lower()
            problem = database.problem_list[problem_code]
            if value not in ["public", "private"]:
                raise ValueError
        except (*exceptions,) as e:
            await info['bot'].send_message(info['channel'], exceptions[type(e)])
            return

        with await database.locks["problem"][problem_code]:
            database.change_problem(problem, "is_public", (value == "public"))
        await info['bot'].send_message(info['channel'], "Successfully made problem `{0}` {1}.".format(problem_code, value))

    async def delete(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "delete problems"):
            return
        try:
            problem_code = info['content'][0].lower()
            if problem_code not in database.problem_list.keys():
                raise ValueError
        except (KeyError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to delete the problem. Please try again.")
        except ValueError:
            await info['bot'].send_message(info['channel'], "Problem `{}` does not exist.".format(problem_code))

        with await database.locks["problem"][problem_code]:
            database.delete_problem(database.problem_list[problem_code])
        await info['bot'].send_message(info['channel'], "Successfully deleted problem `{}`.".format(problem_code))

    async def submit(self, info, contest=None):
        if len(info['message'].attachments) < 1:
            await info['bot'].send_message(info['channel'], "Please upload one file for judging in the message.")
            return
        url = info['message'].attachments[0]["url"]
        submission_time = datetime.datetime.now()

        exceptions = {
            IndexError: "Please select a problem to submit the code to.",
            KeyError: "Invalid problem code.",
            UnicodeDecodeError: "Please upload a valid code file.",
            ValueError: "Please upload a file less than 65536 characters.",
        }
        try:
            problem_code = info['content'][0]
            problem = database.problem_list[problem_code]
            if contest is not None and get_element(contest.contest.problems, problem) is None:
                raise KeyError
            code = requests.get(url).content.decode("utf-8")
            if len(code) > 65536:
                raise ValueError
        except (*exceptions,) as e:
            await info['bot'].send_message(info['channel'], exceptions[type(e)])
            return
        finally:
            try:
                await info['bot'].delete_message(info['message'])
            except errors.Forbidden:
                pass
        if not await has_perm(info['bot'], info['channel'], info['user'], "submit to private problems", not problem.is_public and contest is None):
            return
        id = database.create_submission(models.Submission(None, result="QU", user=info['user'].id, problem=problem_code, submission_time=submission_time, source=code, contest=contest))
        database.judgeserver.judges.judge(id, problem, judge_lang[info['user'].language], code)
        await info['bot'].send_message(info['channel'], "{0}, Submitting code to `{1}`. Please wait.".format(info['user'].discord_user.mention, problem_code))
        await info['bot'].loop.create_task(wait_submission_finish(info['bot'], info['channel'], id, info['user'], contest))
