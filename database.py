import json
import os
import sys
from sortedcontainers import SortedSet

contest_list = {}
problem_list = {}
discord_users_list = {}
judge_list = []
users = {}
games = {}
submission_list = None
judgeserver = None

id = 1

async def load(bot):
    global id
    global problem_list
    global contest_list
    global submission_list
    global discord_users_list
    global users
 
    try:
        with open("bot.json", "r") as f:
            d = json.loads(f.read())
            id = int(d["id"])
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        print("Cannot read the bots settings file. Using defaults.", file=sys.stderr)
    from models import Problem, Contest, Submission, Player, Judge
    try:
        with open("judges/auth", "r") as f:
            for x in f.read().split('\n'):
                try:
                    judge_list.append(Judge(x.split(' ')[0], x.split(' ')[1]))
                except IndexError:
                    pass
    except (FileNotFoundError, KeyError):
        print("Warning: judge authentication keys could not be loaded.", file=sys.stderr)

    problem_list = {x.split(".")[0] : Problem.read(x.split(".")[0]) for x in os.listdir("problems")}
    contest_list = {x.split(".")[0] : Contest.read(x.split(".")[0]) for x in os.listdir("contests")}
    for x in os.listdir("players"):
        x = x.split(".")
        if x[1] == "json":
            discord_users_list[x[0]] = await bot.get_user_info(x[0])
            users[x[0]] = Player.read(x[0])
    submission_list = SortedSet([Submission.read(x.split(".")[0]) for x in os.listdir("submissions") if x.split(".")[1] == "json"], key=lambda x: -x.submission_id)

def save():
    global id
    global problem_list
    global contest_list
    global submission_list
    global judge_list
    global users
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
    with open("judges/auth", "w") as f:
        for x in judge_list:
            f.write(str(x) + "\n")
