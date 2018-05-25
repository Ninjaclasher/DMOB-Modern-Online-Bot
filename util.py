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
        return(str(secs//86400) + " day" + plural(secs//86400) + " " + to_time(secs%86400)).strip()
def to_memory(kilobyte):
    if kilobyte < 2**10:
        return str(kilobyte) + "KB"
    elif kilobyte < 2**20:
        return str(round(kilobyte/float(2**10),2)) + "MB"
    elif kilobyte < 2**30:
        return str(round(kilobyte/float(2**20),2)) + "GB"
    raise ValueError

COMMAND_PREFIX = "&"
BOT_COLOUR = 0x4286F4
DEFAULT_LANG = "cpp11"

help_list = {
    "help": "This command",
    "contest (subcommand)": "Manages a contest. Type `" + COMMAND_PREFIX + "contest help` for subcommands.",
    "language (subcommand)": "Manages your preferred language settings. Type `" + COMMAND_PREFIX + "language help` for subcommands.",
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
