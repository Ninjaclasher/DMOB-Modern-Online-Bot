import math
import sys
import os
import random
import threading
import asyncio

from bridge import JudgeHandler, JudgeServer
from discord import *
from DMOBGame import *
from models import Contest, Problem, Player, Submission
from sortedcontainers import SortedSet
from util import *

import lists

two_commands = ["contest", "language", "submissions"]

BRIDGED_IP_ADDRESS = [('localhost', 9997)]

bot = Client()
judge = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
id = (max(map(int, [x.split(".")[0] for x in os.listdir("submissions")])) if len(os.listdir("submissions")) > 0 else 0) + 1
lock  = asyncio.Lock()

async def load_lists():
    for x in os.listdir("problems"):
        lists.problem_list[x.split(".")[0]] = Problem.read(x.split(".")[0])
    for x in os.listdir("contests"):
        lists.contest_list[x.split(".")[0]] = Contest.read(x.split(".")[0])
    for x in os.listdir("players"):
        x = x.split(".")
        if x[1] == "json":
            lists.discord_users_list[x[0]] = await bot.get_user_info(x[0])
            lists.users[x[0]] = Player.read(x[0])
    lists.submission_list = SortedSet([Submission.read(x.split(".")[0]) for x in os.listdir("submissions")], key=lambda x: -x.submission_id)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    threading.Thread(target=judge.serve_forever).start()
    await load_lists()

games = {}

async def process_command(send, message, command, content):
    global id
    global lock
    try:
        game = games[message.channel]
    except KeyError:
        game = games[message.channel] = DMOBGame(bot, message.channel, judge)
    try:
        user = lists.users[message.author.id]
    except KeyError:
        user = lists.users[message.author.id] = Player(message.author.id,0,0,DEFAULT_LANG,0)
    if command in two_commands:
        try:
            second_command = content[0].lower()
            del content[0]
        except IndexError:
            await bot.send_message(message.channel, "Please enter a subcommand.")
            return
    if command == "help":
        em = Embed(title="Help",description="Available commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list.items():
            em.add_field(name=COMMAND_PREFIX + key, value=value)
        await bot.send_message(message.channel,embed=em)
    elif command == "contest":
        if second_command == "help":
            em = Embed(title="Contest Help",description="Available Contest commands from DMOB", color=BOT_COLOUR)
            for key, value in contest_help_list.items():
                em.add_field(name=COMMAND_PREFIX + "contest " + key, value=value)
            await bot.send_message(message.channel,embed=em)
            return
        elif second_command == "start":
            if len(content) < 1:
                await bot.send_message(message.channel, "Please select a contest to run.")
            else:
                try:
                    c = lists.contest_list[content[0].lower()]
                except KeyError:
                    await bot.send_message(message.channel, "Please enter a valid contest.")
                    return
                try:
                    if int(content[1]) < 1 or int(content[1]) > 31536000:
                        raise ValueError
                    await game.start_round(c, int(content[1]))
                except (IndexError, ValueError):
                    await game.start_round(c)
            return
        elif second_command == "list":
            em = Embed(title="Contest List", description="List of available contests.", color=BOT_COLOUR)
            for x in lists.contest_list.values():
                em.add_field(name=x.name, value="\n".join(y.problem_name for y in x.problems))
            await bot.send_message(message.channel, embed=em)
            return
        if not await game.check_contest_running():
            return
        
        if second_command == "join":
            await game.join(user)
            return
        elif second_command == "rankings":
            await game.rankings()
            return
        elif second_command == "info":
            await game.info()
            return
        elif second_command == "end":
            await game.end_round()
            return

        if not await game.in_contest(user):
            await bot.send_message(message.channel, "You are not in this contest! Please join first.")
            return

        if second_command == "submit":
            if len(message.attachments) != 1:
                await bot.send_message(message.channel, "Please upload one file for judging.")
            elif len(content) != 1:
                await bot.send_message(message.channel, "Please select a problem to submit the code to.")
            else:
                with await lock:
                    this_id = id
                    id += 1
                await game.submit(message, user, content[0], message.attachments[0]["url"], this_id)
        elif second_command == "problem":
            await game.display_problem(user, content[0].strip().lower() if len(content) > 0 else " ")
    elif command == "language":
        call = {
            'help'   : Language.help,
            'list'   : Language.list,
            'change' : Language.change,
            'current': Language.current,
        }
        info = {
            'bot'    : bot,
            'channel': message.channel,
            'user'   : user,
            'content': content,
        }
        try:
            await call[second_command](info)
        except KeyError:
            pass
    elif command == "submissions":
        call = {
            'help'   : Submissions.help,
            'list'   : Submissions.list,
            'view'   : Submissions.view,
            'delete' : Submissions.delete,
        }
        info = {
            'bot'    : bot,
            'channel': message.channel,
            'user'   : user,
            'content': content,
        }
        try:
            await call[second_command](info)
        except KeyError:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX):].strip().split(" ")
        command = stripped_message[0]
        await process_command(bot.send_message, message, command, stripped_message[1:])

token = ""

try:
    bot.loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    for x in lists.users.values():
        x.save()
    for x in lists.contest_list.values():
        x.save()
    for x in lists.problem_list.values():
        x.save()
    for x in lists.submission_list:
        x.save()
    judge.stop()
finally:
    bot.loop.close()
