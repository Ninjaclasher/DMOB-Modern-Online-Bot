from discord import *
from util import *
import asyncio
import database
import models
import os
import requests
import time

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

class Problem:
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
    @staticmethod
    async def help(info):
        em = Embed(title="Problem Help",description="Available Problem commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list["problem"].items():
            em.add_field(name=COMMAND_PREFIX + "problem " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        try:
            page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
            elements_per_page = 9
            if page_num < 1 or (page_num-1)*elements_per_page > len(database.problem_list):
                raise ValueError
            em = Embed(title="Problems",description="Problem page " + str(page_num), color=BOT_COLOUR)
            current_list = list(database.problem_list.values())[(page_num-1)*elements_per_page : min(page_num*elements_per_page, len(database.problem_list))]
            em.add_field(name="Problem Name", value = '\n'.join(x.problem_name for x in current_list))
            em.add_field(name="Problem Code", value = '\n'.join(x.problem_code for x in current_list))
            em.add_field(name="Is Public", value = '\n'.join("Y" if x.is_public else "N" for x in current_list))
            await info['bot'].send_message(info['channel'], embed=em)
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Please enter a valid page number.")

    @staticmethod
    async def view(info):
        try:
            problem = get_element(list(database.problem_list.values()), models.Problem(info['content'][0]))
            if problem is None:
                raise KeyError
        except (ValueError, KeyError):
            await info['bot'].send_message(info['channel'], "Please enter a valid problem code.")
            return
        is_contest = "is_contest" in info.keys() and info["is_contest"]
        if not info['user'].is_admin and not problem.is_public and is_contest:
            await info['bot'].send_message(info['channel'], "You do not have permission to view this problem.")
            return
        try:
            em = Embed(title="Problem Details", description=info['description'], color=BOT_COLOUR)
        except KeyError:
            em = Embed(title="Problem Details", description="Details on problem `" + problem.problem_code + "`", color=BOT_COLOUR)
        em = Embed(title="Problem Info", description="`" + problem.problem_code + "` problem info.")
        em.add_field(name="Problem Name", value=problem.problem_name)
        em.add_field(name="Problem Code", value=problem.problem_code)
        em.add_field(name="Point Value", value=str(problem.point_value if not is_contest else 100) + "p")   
        em.add_field(name="Time Limit", value=str(problem.time) + "s")
        em.add_field(name="Memory Limit", value=to_memory(problem.memory))
        if not is_contest and info['user'].is_admin:
            em.add_field(name="Is Public", value="Y" if problem.is_public else "N")
        await info['bot'].send_message(info['channel'], info['user'].discord_user.mention + ", problem statement has been sent to your private messages.")
        await info['bot'].send_message(info['user'].discord_user, embed=em)
        await info['bot'].send_file(info['user'].discord_user, problem.file)

    @staticmethod
    async def add(info):
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to add a new problem.")
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
            if problem_code in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "A problem with problem code `" + problem_code + "` already exists. Please try again.")
                return
            problem_name = content[1].replace("_", " ")
            point_value, time_limit, memory_limit = map(int, content[2:])
            database.problem_list[problem_code] = models.Problem(problem_code, problem_name, point_value, time_limit, memory_limit, 0)
            os.mkdir("problems/" + problem_code)
            with open("problems/" + problem_code + "/" + problem_code + ".pdf", "wb") as f:
                f.write(requests.get(info['message'].attachments[0]['url']).content)
            await info['bot'].send_message(info['channel'], "Problem `" + problem_code + "` successfully created!")
        except (KeyError, ValueError, IndexError, requests.HTTPError):
            await info['bot'].send_message(info['channel'], "Cannot parse the message content to create a new problem. Please try again.") 

    @staticmethod
    async def change(info):
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to change problems.")
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
            problem = get_element(list(database.problem_list.values()), models.Problem(problem_code))
            if problem is None:
                await info['bot'].send_message(info['channel'], "Problem `" + problem_code + "` does not exist.")
                return
            if field in unchangeable_problem_fields or field not in problem.__dict__.keys():
                await info['bot'].send_message(info['channel'], "Cannot change field `" + content[1] + "`. Please try again.")
                return
            problem.__dict__[field] = int(content[2]) if field != "problem_code" else content[2].replace("_", " ")
            await info['bot'].send_message(info['channel'], "Successfully changed problem `" + problem_code + "`.")
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to change the problem. Please try again.")

    @staticmethod
    async def make(info):
        if not info['user'].is_admin:
            await info['bot'].send_messsage(info['channel'], "You do not have permission to change the problem's visibility.")
            return
        try:
            content = info['content']
            command = content[0].lower()
            if command not in ["public", "private"]:
                raise ValueError
            problem_code = content[1].lower()
            problem = get_element(list(database.problem_list.values()), models.Problem(problem_code))
            if problem is None:
                await info['bot'].send_message(info['channel'], "Problem `" + problem_code + "` does not exist.")
                return
            elif problem.is_public == int(command == "public"):
                await info['bot'].send_message(info['channel'], "Problem `" + problem_code + "` is already " + command + ".")
                return
            problem.is_public = int(command == "public")
            await info['bot'].send_message(info['channel'], "Successfully made problem `" + problem_code + "` " + command + ".")
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to delete the problem. Please try again.")

    @staticmethod
    async def delete(info):
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to delete problems.")
            return
        try:
            content = info['content']
            problem_code = content[0].lower()
            if problem_code not in database.problem_list.keys():
                await info['bot'].send_message(info['channel'], "Problem `" + problem_code + "` does not exist.")
                return
            os.system("mv problems/" + problem_code + " deleted_problems/" + problem_code + "_" + str(int(time.time())))
            await info['bot'].send_message(info['channel'], "Successfully deleted problem `" + problem_code + "`.")
            database.problem_list.pop(problem_code)
        except (KeyError, ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Failed to parse the message content to delete the problem. Please try again.")        

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
            for x in database.submission_list[(page_num-1)*elements_per_page : min(page_num*elements_per_page, len(database.submission_list))]:
                values = ["By: " + str(x.user.discord_user), "Problem: " + str(x.problem.problem_name), "Score: " + str(x.points) + "/" + str(x.total), "Verdict: " + x.result + " (" + verdicts[x.result] + ")"]
                em.add_field(name="Submission #" + str(x.submission_id), value='\n'.join(values))
            await info['bot'].send_message(info['channel'], embed=em)
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Please enter a valid page number.")

    @staticmethod
    async def view(info):
        try:
            sub = get_element(database.submission_list, models.Submission(int(info['content'][0])))
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

class Judge:
    @staticmethod
    async def help(info):
        pass

    @staticmethod
    async def list(info):
        online_judges = [x.name for x in database.judgeserver.judges.judges]
        offline_judges = [x for x in database.judge_list if x.id not in online_judges] if info['user'].is_admin else []
        judge_name = ["✓ " + x for x in online_judges] + [x.id for x in offline_judges]
        judge_ping = [str(round(x.latency,3)) if x.latency is not None else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        judge_load = [str(round(x.load, 3)) if x.latency is not None else "N/A" for x in database.judgeserver.judges.judges] + ["N/A"]*len(offline_judges)
        
        em = Embed(title="Judges", description="List of judges.")
        em.add_field(name="Judge Name", value="\n".join(judge_name))
        em.add_field(name="Ping", value="\n".join(judge_ping))
        em.add_field(name="Load", value="\n".join(judge_load))
        await info['bot'].send_message(info['channel'], embed=em)
    
    @staticmethod
    async def view(info):
        try:
            judge_name = info['content'][0].lower()
            online_judges = [x.name.lower() for x in database.judgeserver.judges.judges]
            if judge_name not in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `" + info['content'][0] + "` does not exist.")
                return
            em = Embed(title="Judge Info", description=judge_name.capitalize() + " Details", color=BOT_COLOUR)
            fields = {
                    "Judge Name": ("✓ " if judge_name in online_judges else "") + judge_name.capitalize(),
                    "Ping"      : "N/A",
                    "Load"      : "N/A",
                    "Supported Languages" : "N/A",
            }
            if judge_name in online_judges:
                for x in database.judgeserver.judges.judges:
                    if x.name.lower() == judge_name:
                        fields["Ping"] = round(x.latency, 3) if x.latency is not None else "N/A"
                        fields["Load"] = round(x.load, 3) if x.load is not None else "N/A"
                        fields["Supported Languages"] = ", ".join(dmob_lang[y] for y in x.executors.keys() if y in dmob_lang.keys())
                        break
            for x, y in fields.items():
                em.add_field(name=x, value=y)
            await info['bot'].send_message(info['channel'], embed=em)    
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a judge name")
    
    @staticmethod
    async def add(info):
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to add judges.")
            return
        try:
            judge_name = info['content'][0]
            judge_key = info['content'][1]
            await info['bot'].delete_message(info['message'])
            if judge_name.lower() in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `" + judge_name + "` already exists.")
                return
            database.judge_list.append(models.Judge(judge_name, judge_key))
            await info['bot'].send_message(info['channel'], "Judge `" + judge_name + "` successfully added!")
        except IndexError:
            await info['bot'].send_message(info['channel'], "Could not parse message content and add a judge. Please try again.")

    @staticmethod
    async def delete(info):
        if not info['user'].is_admin:
            await info['bot'].send_message(info['channel'], "You do not have permission to delete judges.")
            return
        try:
            judge_name = info['content'][0]
            if not judge_name.lower() in [x.id.lower() for x in database.judge_list]:
                await info['bot'].send_message(info['channel'], "Judge with name `" + judge_name + "` does not exist.")
                return
            for x in range(len(database.judge_list)):
                if database.judge_list[x].id.lower() == judge_name.lower():
                    del database.judge_list[x]
            await info['bot'].send_message(info['channel'], "Judge `" + judge_name + "`successfully deleted!")
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid judge name.")
