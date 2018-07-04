import math
import time

from bisect import bisect

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
    byte = ["K", "M", "G", "T", "P", "E", "Z"]
    if kilobyte < 0:
        raise ValueError("Kilobyte cannot be negative.")
    elif kilobyte == 0:
        return "0B"
    elif kilobyte > 2**(len(byte)*10):
        raise ValueError("Kilobyte is too large.")
        
    i  = bisect([2**(10*x) for x in range(len(byte))], kilobyte) - 1
    return "{0}{1}B".format(round(kilobyte/float(2**(i*10)), 2), byte[i])

def get_element(arr, val):
    for x in arr:
        if x == val:
            return x
    return None

def rational_approximation(t):
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    numerator = (c[2] * t + c[1]) * t + c[0]
    denominator = ((d[2] * t + d[1]) * t + d[0]) * t + 1.0
    return t - numerator / denominator

def normal_CDF_inverse(p):
    assert 0.0 < p < 1
    if p < 0.5:
        return -rational_approximation(math.sqrt(-2.0 * math.log(p)))
    else:
        return rational_approximation(math.sqrt(-2.0 * math.log(1.0 - p)))

def WP(RA, RB, VA, VB):
    return (math.erf((RB - RA) / math.sqrt(2 * (VA * VA + VB * VB))) + 1) / 2.0

def recalculate_ratings(old_rating, old_volatility, actual_rank, times_rated):
    # actual_rank: 1 is first place, N is last place
    # if there are ties, use the average of places (if places 2, 3, 4, 5 tie, use 3.5 for all of them)

    N = len(old_rating)
    new_rating = old_rating[:]
    new_volatility = old_volatility[:]
    if N <= 1:
        return new_rating, new_volatility

    ave_rating = float(sum(old_rating)) / N
    sum1 = sum(i * i for i in old_volatility) / N
    sum2 = sum((i - ave_rating) ** 2 for i in old_rating) / (N - 1)
    CF = math.sqrt(sum1 + sum2)

    for i in range(N):
        ERank = 0.5
        for j in range(N):
            ERank += WP(old_rating[i], old_rating[j], old_volatility[i], old_volatility[j])

        EPerf = -normal_CDF_inverse((ERank - 0.5) / N)
        APerf = -normal_CDF_inverse((actual_rank[i] - 0.5) / N)
        PerfAs = old_rating[i] + CF * (APerf - EPerf)
        Weight = 1.0 / (1 - (0.42 / (times_rated[i] + 1) + 0.18)) - 1.0
        if old_rating[i] > 2500:
            Weight *= 0.8
        elif old_rating[i] >= 2000:
            Weight *= 0.9

        Cap = 150.0 + 1500.0 / (times_rated[i] + 2)

        if times_rated[i] == 0:
            new_volatility[i] = 385
        else:
            new_volatility[i] = math.sqrt(((new_rating[i] - old_rating[i]) ** 2) / Weight + (old_volatility[i] ** 2) / (Weight + 1))
        new_rating[i] = (old_rating[i] + Weight * PerfAs) / (1.0 + Weight)
        if abs(old_rating[i] - new_rating[i]) > Cap:
            if old_rating[i] < new_rating[i]:
                new_rating[i] = old_rating[i] + Cap
            else:
                new_rating[i] = old_rating[i] - Cap

    # try to keep the sum of ratings constant
    adjust = float(sum(old_rating) - sum(new_rating)) / N
    new_rating = list(map(adjust.__add__, new_rating))
    # inflate a little if we have to so people who placed first don't lose rating
    best_rank = min(actual_rank)
    for i in range(N):
        if abs(actual_rank[i] - best_rank) <= 1e-3 and new_rating[i] < old_rating[i] + 1:
            new_rating[i] = old_rating[i] + 1
    return list(map(int, map(round, new_rating))), list(map(int, map(round, new_volatility)))


async def has_perm(bot, channel, user, message, alternate_condition=True, no_perm_message=True):
    if not user.is_admin and alternate_condition:
        if no_perm_message:
             await bot.send_message(channel, "You do not have permission to {}.".format(message))
        return False
    return True

async def get_current_list(info, arr, elements_per_page=9):
    try:
        page_num = int(info['content'][0]) if len(info['content']) > 0 else 1
        if (page_num < 1 or (page_num-1)*elements_per_page >= len(arr)) and page_num != 1:
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
    "change (problem code) (field to change) (new value)": "Change a problem. Please do `" + COMMAND_PREFIX + "problem change help` for details on how to use this command.",
    "make {public, private} (problem_code)" : "Make a problem private/public to normal users.",
    "delete (problem code)"                 : "Deletes a problem.",
    "submit (problem code)"                 : "Submit to a problem.",
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
    "start (judge name)"                    : "Starts a judge.",
    "stop (juge name)"                      : "Stops a judge.",
}
help_list["user"] = {
    "help"                                  : "Displays this message.",
    "list [page number]"                    : "Lists all users with a non-zero point value.",
    "view [user]"                           : "Views details on a user.",
    "submissions [user] [page number]"      : "Views a page of submissions by a user.",
    "make {admin, normal} (user)"           : "Make a user an admin or a normal user.",
    "reset (user)"                          : "Resets a user to the default values.",
}

unchangeable_problem_fields = {"problem_code", "is_public", "_user", "id"}

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

VERDICT_FULL = {
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
    'QU'    : 'Processing',
}

VERDICT_COLOUR = {
    'AC'    : 0x53F23F,
    'WA'    : 0xEF1B32,
    'TLE'   : 0xC0C0C0,
    'MLE'   : 0xC0C0C0,
    'OLE'   : 0xFAB623,
    'IR'    : 0xFAB623,
    'RTE'   : 0xFAB623,
    'CE'    : 0xC0C0C0,
    'IE'    : 0xFF0000,
    'SC'    : 0xC0C0C0,
    'AB'    : 0xC0C0C0,
    'QU'    : 0xC0C0C0,
}

