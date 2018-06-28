from .BaseHandler import BaseHandler
from discord import *
from util import *
import database
import models
import os
import requests
import time

class Problem(BaseHandler):
    command_help = {}
    command_help["add"] = [
        ["Command",  "`" + COMMAND_PREFIX + "problem add (problem code) (problem name) (point value) (time limit) (memory limit)`"],
        ["Details", "Please include a file when adding the problem as the problem statement."],
        ["problem code", "The problem code that the problem should have. This should be unique with all problems."],
        ["problem name", "The user readable problem name. When adding a problem, please use `_` to represent spaces as there cannot be spaces in the problem name."],
        ["point value", "An integer value for the point value of the problem."],
        ["time limit", "An integer value for the time limit (in seconds) of the problem."],
        ["memory limit", "An integer value for the memory limit (in kilobytes) of the problem."],
    ]
    command_help["change"] = [
        ["Command", "`" + COMMAND_PREFIX + "problem change (problem code) (field to change) (new value)`"],
        ["problem code", "The problem code for the problem to change."],
        ["field to change", "The field in the problem to change. Possible fields are: [`" + "`, `".join(delete_elements(list(models.Problem("").__dict__.keys()), unchangeable_problem_fields)) + "`]"],
        ["new value", "The new value for the field specified."],
    ]
    async def list(self, info):
        current_list, page_num = await get_current_list(info, list(database.problem_list.values()), 30)
        current_list.sort(key = lambda x: x.problem_name)
        if current_list is None:
            return
        em = Embed(title="Problems",description="Problem page {}".format(page_num), color=BOT_COLOUR)
        em.add_field(name="Problem Name", value = '\n'.join(x.problem_name for x in current_list))
        em.add_field(name="Problem Code", value = '\n'.join(x.problem_code for x in current_list))
        em.add_field(name="Is Public", value = '\n'.join("Y" if x.is_public else "N" for x in current_list))
        await info['bot'].send_message(info['channel'], embed=em)

    async def view(self, info):
        is_contest = "is_contest" in info.keys() and info["is_contest"]
        if len(info['content']) < 1:
            await info['bot'].send_message(info['channel'], "Please enter a problem code.")
            return
        problem_code = info['content'][0].lower()
        with await database.locks["problem"][problem_code]:
            try:
                problem = get_element(list(database.problem_list.values()), models.Problem(problem_code))
                if problem is None:
                    raise KeyError
            except (ValueError, KeyError):
                await info['bot'].send_message(info['channel'], "Please enter a valid problem code.")
                return
            if not await has_perm(info['bot'], info['channel'], info['user'], "view this problem", not problem.is_public and not is_contest):
                return
            try:
                em = Embed(title="Problem Details", description=info['description'], color=BOT_COLOUR)
            except KeyError:
                em = Embed(title="Problem Details", description="Details on problem `{}`".format(problem.problem_code), color=BOT_COLOUR)
            em = Embed(title="Problem Info", description="`{}` problem info.".format(problem.problem_code))
            em.add_field(name="Problem Name", value=problem.problem_name)
            em.add_field(name="Problem Code", value=problem.problem_code)
            em.add_field(name="Point Value", value="{}p".format(problem.point_value if not is_contest else 100))   
            em.add_field(name="Time Limit", value="{}s".format(problem.time))
            em.add_field(name="Memory Limit", value=to_memory(problem.memory))
            if not is_contest and info['user'].is_admin:
                em.add_field(name="Is Public", value="Y" if problem.is_public else "N")
       
        await info['bot'].send_message(info['user'].discord_user, embed=em)
        await info['bot'].send_file(info['user'].discord_user, problem.file)
        await info['bot'].send_message(info['channel'], "{}, problem statement has been sent to your private messages.".format(info['user'].discord_user.mention))

    async def add(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "add problems"):
            return
        try:
            content = info['content']
            if len(content) == 1 and content[0].lower() == "help":
                em = Embed(title="Problem Adding Help", description="Details on how to add a problem.", color=BOT_COLOUR)
                for x in Problem().command_help["add"]:
                    em.add_field(name=x[0], value=x[1])
                await info['bot'].send_message(info['channel'], embed=em)
                return

            if len(info['message'].attachments) != 1:
                await info['bot'].send_message(info['channel'], "Please upload one file for the problem statement.")
                return 
            problem_code = content[0].lower()
        except (KeyError, ValueError, IndexError, requests.HTTPError):
            await info['bot'].send_message(info['channel'], "Cannot parse the message content to create a new problem. Please try again.") 
        with await database.locks["problem"][problem_code]:
            if problem_code in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "A problem with problem code `{}` already exists. Please try again.".format(problem_code))
                return
            problem_name = content[1].replace("_", " ")
            point_value, time_limit, memory_limit = map(int, content[2:])
            database.problem_list[problem_code] = models.Problem(problem_code, problem_name, point_value, time_limit, memory_limit, 0)
            os.mkdir("problems/{}".format(problem_code))
            with open("problems/{0}/{0}.pdf".format(problem_code), "wb") as f:
                f.write(requests.get(info['message'].attachments[0]['url']).content)
        await info['bot'].send_message(info['channel'], "Problem `{}` successfully created!".format(problem_code))

    async def change(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "change problems"):
            return
        try:
            content = info['content']
            if len(content) == 1 and content[0].lower() == "help":
                em = Embed(title="Problem Changing Help", description="Details on how to change a problem.", color=BOT_COLOUR)
                for x in Problem().command_help["change"]:
                    em.add_field(name=x[0], value=x[1])
                await info['bot'].send_message(info['channel'], embed=em)
                return
            problem_code = content[0].lower()
            field = content[1].lower()
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to change the problem. Please try again.")
        with await database.locks["problem"][problem_code]:
            problem = get_element(list(database.problem_list.values()), models.Problem(problem_code))
            if problem is None:
                await info['bot'].send_message(info['channel'], "Problem `{}` does not exist.".format(problem_code))
                return
            elif field in unchangeable_problem_fields or field not in problem.__dict__.keys():
                await info['bot'].send_message(info['channel'], "Cannot change field `{}`. Please try again.".format(content[1]))
                return
            problem.__dict__[field] = int(content[2]) if field != "problem_name" else content[2].replace("_", " ")
        await info['bot'].send_message(info['channel'], "Successfully changed problem `{}`.".format(problem_code))

    async def make(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "change a problem's visibility"):
            return
        try:
            value = info['content'][0].lower()
            problem_code = info['content'][1].lower()
            if value not in ["public", "private"]:
                raise ValueError
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to change the problem. Please try again.")
        with await database.locks["problem"][problem_code]:
            problem = get_element(list(database.problem_list.values()), models.Problem(problem_code))
            if problem is None:
                await info['bot'].send_message(info['channel'], "Problem `{}` does not exist.".format(problem_code))
                return
            elif problem.is_public == int(value == "public"):
                await info['bot'].send_message(info['channel'], "Problem `{0}` is already {1}.".format(problem_code, value))
                return
            problem.is_public = int(value == "public")
        await info['bot'].send_message(info['channel'], "Successfully made problem `{0}` {1}.".format(problem_code, value))

    async def delete(self, info):
        if not await has_perm(info['bot'], info['channel'], info['user'], "delete problems"):
            return            
        try:
            content = info['content']
            problem_code = content[0].lower()
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to delete the problem. Please try again.")        

        with await database.locks["problem"][problem_code]:
            if problem_code not in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "Problem `{}` does not exist.".format(problem_code))
                return
            os.system("mv problems/{0} deleted_problems/{0}_{1}".format(problem_code, int(time.time())))
            database.problem_list.pop(problem_code)
        await info['bot'].send_message(info['channel'], "Successfully deleted problem `{}`.".format(problem_code))
