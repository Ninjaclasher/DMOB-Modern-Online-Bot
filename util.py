def plural(num):
    return "s" if num != 1 else ""

def to_time(secs):
    if secs == 0:
        return ""
    elif secs < 60:
        return str(secs) + " second" + plural(secs)
    elif secs < 3600:
        return (str(secs//60) + " minute" + plural(secs//60) + " " + to_time(secs%60)).strip()
    elif secs < 86400:
        return (str(secs//3600) + " hour" + plural(secs//3600) + " " + to_time(secs%3600)).strip()
    elif secs < 604800:
        return (str(secs//86400) + " day" + plural(secs//86400) + " " + to_time(secs%86400)).strip()
    elif secs < 2419200:
        return (str(secs//604800) + " week" + plural(secs//604800) + " " + to_time(secs%604800)).strip()
        
def to_memory(kilobyte):
    if kilobyte < 0:
        raise ValueError("Kilobyte cannot be negative.")
    byte = ["K", "M", "G", "T", "P", "E", "Z"]
    for i, j in enumerate(byte, 1):
        if kilobyte >= 2**(i*10):
            continue
        return str(round(kilobyte/float(2**((i-1)*10)),2)) + j + "B"
    raise ValueError("Kilobyte is too large.")

def get_element(arr, val):
    for x in arr:
        if x == val:
            return x
    return None

COMMAND_PREFIX = "&"
BOT_COLOUR = 0x4286F4
DEFAULT_LANG = "cpp11"

help_list = {
    "help": "This command",
    "contest (subcommand)": "Manages a contest. Type `" + COMMAND_PREFIX + "contest help` for subcommands.",
    "language (subcommand)": "Manages your preferred language settings. Type `" + COMMAND_PREFIX + "language help` for subcommands.",
    "submissions (subcommand)": "Manages submissions. Type `" + COMMAND_PREFIX + "submissions help` for subcommands.", 
}
contest_help_list = {
    "help": "Displays this message.",
    "start (contest name) [time window]": "Starts a contest for the specified amount of time. Defaults to 3 hours.",
    "end": "Ends the contest.",
    "list": "Lists the available contests.",
    "submit (problem code)": "Submit to a problem.",
    "problem [problem code]": "View the problem statement for a problem. Enter no problem code to list all the problems in the contest.",
    "join": "Join the contest.",
    "rankings": "View the current leaderboard for the contest.",
    "info": "Displays information on the contest.",
}
language_help_list = {
    "help": "Displays this message.",
    "list": "List the available language options.",
    "current": "Displays your current preferred language.",
    "change (language code)": "Change your preferred language to the specified language.",
}
submissions_help_list = {
    "help": "Displays this message",
    "list (page number)": "Lists a page of submissions.",
    "view (submission id)": "Views details on a submission.",
    "delete (submission id)" : "Deletes a submission.",
}

languages = ["c", "c11", "cpp03", "cpp11", "cpp14", "cpp17", "java8", "turing", "python2", "python3", "pypy3", "pypy3"]
judge_lang = {
    "c": "C",
    "c11": "C11",
    "cpp03": "CPP03",
    "cpp11": "CPP11",
    "cpp14": "CPP14",
    "cpp17": "CPP17",
    "java8": "JAVA8",
    "turing": "TUR",
    "python2": "PY2",
    "python3": "PY3",
    "pypy2": "PYPY",
    "pypy3": "PYPY3",
}

verdicts = {
    'AC': 'Accepted',
    'WA': 'Wrong Answer',
    'TLE': 'Time Limit Exceeded',
    'MLE': 'Memory Limit Exceeded',
    'OLE': 'Output Limit Exceeded',
    'IR': 'Invalid Return',
    'RTE': 'Runtime Error',
    'CE': 'Compile Error',
    'IE': 'Internal Error',
    'SC': 'Short circuit',
    'AB': 'Aborted',
}

from discord import *
from models import Submission
import lists

class Language:
    @staticmethod
    async def help(info):
        em = Embed(title="Language Help",description="Available Language commands from DMOB", color=BOT_COLOUR)
        for key, value in language_help_list.items():
            em.add_field(name=COMMAND_PREFIX + "language " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        em = Embed(title="Language List", description="List of available languages", color=BOT_COLOUR)
        em.add_field(name="Languages", value="\n".join(languages))
        await info['bot'].send_message(info['channel'], embed=em)
    
    @staticmethod
    async def current(info):
        await info['bot'].send_message(info['channel'], "Your current language is `" + info['user'].language + "`")

    @staticmethod
    async def change(info):
        try:
            lang = info['content'][0]
            if not lang in languages:
                raise IndexError
            info['user'].language = lang
            await info['bot'].send_message(info['channel'], "Your language has been changed to `" + lang + '`')
        except IndexError:
            await info['bot'].send_message(info['channel'], "Please enter a valid language.")

class Submissions:
    @staticmethod
    async def help(info):
        em = Embed(title="Submissions Help",description="Available Submissions commands from DMOB", color=BOT_COLOUR)
        for key, value in submissions_help_list.items():
            em.add_field(name=COMMAND_PREFIX + "submissions " + key, value=value)
        await info['bot'].send_message(info['channel'], embed=em)

    @staticmethod
    async def list(info):
        try:
            page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
            elements_per_page = 9
            if page_num < 1 or (page_num-1)*elements_per_page > len(lists.submission_list):
                raise ValueError
            em = Embed(title="Submissions",description="Submission page " + str(page_num), color=BOT_COLOUR)
            for x in range((page_num-1)*elements_per_page, min(page_num*elements_per_page+1, len(lists.submission_list))):
                cur = lists.submission_list[x]
                values = ["By: " + str(cur.user.discord_user), "Problem: " + str(cur.problem.problem_name), "Score: " + str(cur.points) + "/" + str(cur.total), "Verdict: " + cur.result + " (" + verdicts[cur.result] + ")"]
                em.add_field(name="Submission #" + str(cur.submission_id), value='\n'.join(values))
            await info['bot'].send_message(info['channel'], embed=em)
        except (ValueError, IndexError):
            await info['bot'].send_message(info['channel'], "Please enter a valid page number.")

    @staticmethod
    async def view(info):
        try:
            sub = get_element(lists.submission_list, Submission(int(info['content'][0])))
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
    async def delete(info):
        pass

