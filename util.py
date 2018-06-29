import time

def plural(num):
    return "s" if num != 1 else ""

def to_time(secs):
    names = [[60, "minute"], [3600, "hour"], [86400, "day"], [604800, "week"], [2419200, "month"], [31536000, "year"]]
    if secs < 0:
        raise ValueError("Seconds cannot be negative.")
    elif secs == 0:
        return ""
    elif secs < 60:
        return "{0} second{1}".format(secs, plural(secs))
    else:
        for x in range(len(names)-1):
            if names[x][0] <= secs < names[x+1][0]:
                return "{0} {1}{2} {3}".format(secs//names[x][0], names[x][1], plural(secs//names[x][0]), to_time(secs%names[x][0])).strip()

def to_datetime(convert_time):
    return time.strftime('%h %d, %Y %I:%M:%S %p', time.localtime(convert_time))

def to_memory(kilobyte):
    if kilobyte < 0:
        raise ValueError("Kilobyte cannot be negative.")
    byte = ["K", "M", "G", "T", "P", "E", "Z"]
    for i, j in enumerate(byte, 1):
        if kilobyte >= 2**(i*10):
            continue
        return "{0}{1}B".format(round(kilobyte/float(2**((i-1)*10)),2), j)
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

async def has_perm(bot, channel, user, message, alternate_condition=True, no_perm_message=True):
    if not user.is_admin and alternate_condition:
        if no_perm_message:
             await bot.send_message(channel, "You do not have permission to {}.".format(message))
        return False
    return True

async def get_current_list(info, arr, elements_per_page=9):
    try:
        page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
        if page_num < 1 or (page_num-1)*elements_per_page > len(arr):
            raise ValueError
    except (ValueError, IndexError):
        await info['bot'].send_message(info['channel'], "Please enter a valid page number.")
        return None, 0
    return arr[(page_num-1)*elements_per_page : page_num*elements_per_page], page_num

from settings import *

help_list = {}

help_list[""] = {
    "help"                                  : "This command.",
    "contest (subcommand)"                  : "Manages a contest. Type `" + COMMAND_PREFIX + "contest help` for subcommands.",
    "problem (subcommand)"                  : "Manages problems. Type `" + COMMAND_PREFIX + "problem help` for subcommands.",
    "language (subcommand)"                 : "Manages your preferred language settings. Type `" + COMMAND_PREFIX + "language help` for subcommands.",
    "submissions (subcommand)"              : "Manages submissions. Type `" + COMMAND_PREFIX + "submissions help` for subcommands.", 
    "judge (subcommand)"                    : "Manages judges. Type `" + COMMAND_PREFIX + "judge help` for subcommands.",
    "user (subcommand)"                     : "Manages users. Type `" + COMMAND_PREFIX + "user help` for subcommands.",
}
help_list["contest"] = {
    "help"                                  : "Displays this message.",
    "add (contest name) (problem codes)"    : "Creates a contest with (problem codes) set of problems.",
    "delete (contest name)"                 : "Deletes a problem.",
    "start (contest name) [time window]"    : "Starts a contest for the specified amount of time. Defaults to 3 hours.",
    "end"                                   : "Ends the contest.",
    "list [page number]"                    : "Lists the available contests.",
    "submit (problem code)"                 : "Submit to a problem.",
    "problem [problem code]"                : "View the problem statement for a problem. Enter no problem code to list all the problems in the contest.",
    "join"                                  : "Join the contest.",
    "rankings"                              : "View the current leaderboard for the contest.",
    "info"                                  : "Displays information on the contest.",
}
help_list["problem"] = {
    "help"                                  : "Displays this message.",
    "list [page number]"                    : "Lists a page of problems",
    "view (problem code)"                   : "Views details on a problem",
    "add (problem values)"                  : "Adds a problem. Please do `" + COMMAND_PREFIX + "problem add help` for details on how to use this command.",
    'change (problem code) (field to change) (new value)': "Change a problem. Please do `" + COMMAND_PREFIX + "problem change help` for details on how to use this command.",
    "make {public, private} (problem_code)" : "Make a problem private/public to normal users.",
    'delete (problem code)'                 : "Deletes a problem.",
}
help_list["language"] = {
    "help"                                  : "Displays this message.",
    "list"                                  : "List the available language options.",
    "current"                               : "Displays your current preferred language.",
    "change (language code)"                : "Change your preferred language to the specified language.",
}
help_list["submissions"] = {
    "help"                                  : "Displays this message.",
    "list [page number]"                    : "Lists a page of submissions.",
    "view (submission id)"                  : "Views details on a submission.",
    "code (submission id)"                  : "Views the code for a submission.",
    "delete (submission id)"                : "Deletes a submission.",
}
help_list["judge"] = {
    "help"                                  : "Displays this message.",
    "list"                                  : "Lists the judges.",
    "view (judge name)"                     : "Views details on a judge.",
    "add (judge name) (judge key)"          : "Adds a judge.",
    "delete (judge name)"                   : "Deletes a judge.",
}
help_list["user"] = {
    "help"                                  : "Displays this message.",
    "list [page number]"                    : "Lists all users with a non-zero point value.",
    "view (user)"                           : "Views details on a user.",
    "make {admin, normal} (user)"           : "Make a user an admin or a normal user.",
    "reset (user)"                          : "Resets a user to the default values.",
}

unchangeable_problem_fields = ["problem_code", "is_public"]

judge_lang = {
    "c"         : "C",
    "c11"       : "C11",
    "cpp03"     : "CPP03",
    "cpp11"     : "CPP11",
    "cpp14"     : "CPP14",
    "cpp17"     : "CPP17",
    "java8"     : "JAVA8",
    "turing"    : "TUR",
    "python2"   : "PY2",
    "python3"   : "PY3",
    "pypy2"     : "PYPY",
    "pypy3"     : "PYPY3",
}

dmob_lang = {y:x for x, y in judge_lang.items()}

verdicts = {
    'AC'    : 'Accepted',
    'WA'    : 'Wrong Answer',
    'TLE'   : 'Time Limit Exceeded',
    'MLE'   : 'Memory Limit Exceeded',
    'OLE'   : 'Output Limit Exceeded',
    'IR'    : 'Invalid Return',
    'RTE'   : 'Runtime Error',
    'CE'    : 'Compile Error',
    'IE'    : 'Internal Error',
    'SC'    : 'Short circuit',
    'AB'    : 'Aborted',
}

verdict_colours = {
    'AC'    : 0x53F23F,
    'WA'    : 0xEF1B32,
    'TLE'   : 0x0C0C0C,
    'MLE'   : 0x0C0C0C,
    'OLE'   : 0xFAB623,
    'IR'    : 0xFAB623,
    'RTE'   : 0xFAB623,
    'CE'    : 0x0C0C0C,
    'IE'    : 0xFF0000,
    'SC'    : 0x0C0C0C,
    'AB'    : 0x0C0C0C,
}

ranking_titles = [
    [0, "Unrated"],
    [1, "Newbie"],
    [1000, "Amateur"],
    [1200, "Expert"],
    [1500, "Candidate Master"],
    [1800, "Master"],
    [2200, "Grandmaster"],
    [3000, "Hacker"],
    [10**10, ""],
]

ranking_colour = {
    "Unrated"           : 0xFFFFFF,
    None                : 0xFFFFFF,
    "Newbie"            : 0x909090,
    "Amateur"           : 0x00A900,
    "Expert"            : 0x0000FF,
    "Candidate Master"  : 0x800080,
    "Master"            : 0xFFB100,
    "Grandmaster"       : 0x0E0000,
    "Hacker"            : 0xFF0000,
}
