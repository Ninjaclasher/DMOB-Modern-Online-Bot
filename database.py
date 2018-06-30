import asyncio
import json
import os
import sys
import threading
from collections import defaultdict
from settings import *
from sortedcontainers import SortedSet

contest_list = {}
problem_list = {}
discord_users_list = {}
users = {}
games = {}
locks = {}
judge_list = []
submission_list = None
submission_cases_list = None
judgeserver = None
loading = False

id = 1

async def load_user(bot, user_id):
    global users
    global discord_users_list
    try:
        return users[user_id]
    except KeyError:
        discord_users_list[user_id] = await bot.get_user_info(user_id)
        from models import Player
        users[user_id] = Player(user_id)
        return users[user_id]

async def load(bot):
    global loading
    loading = True
    global id
    global problem_list
    global contest_list
    global submission_list
    global submission_cases_list
    global discord_users_list
    global users
    global judgeserver 
    global locks
    try:
        with open("bot.json", "r") as f:
            d = json.loads(f.read())
            id = int(d["id"])
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print("Cannot read the bots settings file. Using defaults.", file=sys.stderr)
    locks["problem"] = defaultdict(lambda: asyncio.Lock())
    locks["submissions"] = defaultdict(lambda: asyncio.Lock())
    locks["judge"] = defaultdict(lambda: asyncio.Lock())
    locks["user"] = defaultdict(lambda: asyncio.Lock())
    locks["contest"] = defaultdict(lambda: asyncio.Lock())
    from bridge import JudgeHandler, JudgeServer
    from models import Problem, Contest, Submission, SubmissionTestCase, Player, Judge
    try:
        with open("judges/auth", "r") as f:
            for x in f.read().split('\n'):
                try:
                    judge_list.append(Judge(x.split(' ')[0], x.split(' ')[1]))
                except IndexError:
                    pass
    except (FileNotFoundError, KeyError):
        print("Warning: judge authentication keys could not be loaded.", file=sys.stderr)

    judgeserver = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
    threading.Thread(target=judgeserver.serve_forever).start()
    problem_list = {x : Problem.read(x) for x in os.listdir("problems")}
    contest_list = {x.split(".")[0] : Contest.read(x.split(".")[0]) for x in os.listdir("contests")}
    for x in os.listdir("players"):
        x = x.split(".")
        if x[1] == "json":
            discord_users_list[x[0]] = await bot.get_user_info(x[0])
            users[x[0]] = Player.read(x[0])
    submission_list = SortedSet([Submission.read(x) for x in os.listdir("submissions")], key=lambda x: -x.submission_id)
    submission_cases_list = defaultdict(lambda: SortedSet([], lambda x: x.case))
    for x in os.listdir("submissions"):
        submission_cases_list[int(x)] = SortedSet([SubmissionTestCase.read(int(x), int(y.split(".")[0])) for y in os.listdir("submissions/{}/cases/".format(x))], key=lambda x: x.case)
    loading = False

async def save():
    global id
    global problem_list
    global contest_list
    global submission_list
    global submission_cases_list    
    global judge_list
    global users
    global judgeserver
    global locks

    for x in locks.values():
        for y in x.values():
            with await y:
                pass
    
    judgeserver.stop()
    with open("bot.json", "w") as f:
        store = {"id": id}
        f.write(str(store).replace("'", "\""))
    for x in users.values():
        x.save()
    for x in contest_list.values():
        x.save()
    for x in problem_list.values():
        x.save()
    for x in submission_list:
        x.save()
    for x in submission_cases_list.values():
        for y in x:
            y.save()
    with open("judges/auth", "w") as f:
        for x in judge_list:
            f.write("{}\n".format(x))
