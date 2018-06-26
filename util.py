import time

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

def to_datetime(convert_time):
    return time.strftime('%h %d, %Y %I:%M:%S %p', time.localtime(convert_time))

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

def delete_elements(arr, delete):
    for x in delete:
        arr.remove(x)
    return arr

from settings import *

help_list = {}

help_list[""] = {
    "help": "This command",
    "contest (subcommand)": "Manages a contest. Type `" + COMMAND_PREFIX + "contest help` for subcommands.",
    "problem (subcommand)": "Manages problems. Type `" + COMMAND_PREFIX + "problem help` for subcommands.",
    "language (subcommand)": "Manages your preferred language settings. Type `" + COMMAND_PREFIX + "language help` for subcommands.",
    "submissions (subcommand)": "Manages submissions. Type `" + COMMAND_PREFIX + "submissions help` for subcommands.", 
    "judge (subcommand)" : "Manages judges. Type `" + COMMAND_PREFIX + "judge help` for subcommands",
}
help_list["contest"] = {
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
help_list["problem"] = {
    "help": "Displays this message.",
    "list [page number]": "Lists a page of problems",
    "view (problem code)": "Views details on a problem",
    "add (problem values)": "Adds a problem. Please do `" + COMMAND_PREFIX + "problem add help` for details on how to use this command.",
    'change (problem code) (field to change) (new value)': "Change a problem. Please do `" + COMMAND_PREFIX + "problem change help` for details on how to use this command.",
    "make {public, private} (problem_code)" : "Make a problem private/public to normal users.",
    'delete (problem code)': "Deletes a problem.",
}
help_list["language"] = {
    "help": "Displays this message.",
    "list": "List the available language options.",
    "current": "Displays your current preferred language.",
    "change (language code)": "Change your preferred language to the specified language.",
}
help_list["submissions"] = {
    "help": "Displays this message.",
    "list [page number]": "Lists a page of submissions.",
    "view (submission id)": "Views details on a submission.",
    "code (submission id)": "Views the code for a submission.",
    "delete (submission id)" : "Deletes a submission.",
}
help_list["judge"] = {
    "help": "Displays this message.",
    "list": "Lists the judges.",
    "view (judge name)": "Views details on a judge.",
    "add (judge name) (judge key)": "Adds a judge",
    "delete (judge name)": "Deletes a judge",
}

unchangeable_problem_fields = ["problem_code", "is_public"]

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

dmob_lang = {y:x for x, y in judge_lang.items()}

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

