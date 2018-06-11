import math
import sys
import os
import random
import threading
import asyncio

from model import Contest, Problem, Player
from bridge import JudgeHandler, JudgeServer
from discord import *
from DMOBGame import *
from util import *

two_commands = ["contest", "language"]
contest_list = [Contest.read(x.split(".")[0]) for x in os.listdir("contests") if x.split(".")[1] == "json"]
problem_list = [Problem.read(x.split(".")[0]) for x in os.listdir("problems")]
users = {}
for x in os.listdir("players"):
    x = x.split(".")
    if x[1] == "json":
        users[x[0]] = Player.read(x[0])

BRIDGED_IP_ADDRESS = [('localhost', 9997)]

bot = Client()
judge = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
id = 1
lock  = asyncio.Lock()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    threading.Thread(target=judge.serve_forever).start()

games = {}

async def process_command(send, message, command, content):
    global id
    global lock
    try:
        game = games[message.channel]
    except KeyError:
        game = games[message.channel] = DMOBGame(bot, message.channel, judge)
    try:
        user = users[message.author.id]
    except KeyError:
        user = users[message.author.id] = Player(message.author.id,0,0,DEFAULT_LANG,0)
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
            elif Contest(content[0].lower(), []) not in contest_list:
                await bot.send_message(message.channel, "Please enter a valid contest.")
            else:
                c = contest_list.index(Contest(content[0].lower(), []))
                try:
                    if int(content[1]) < 1 or int(content[1]) > 31536000:
                        raise ValueError
                    await game.start_round(contest_list[c], int(content[1]))
                except (IndexError, ValueError):
                    await game.start_round(contest_list[c])
            return
        elif second_command == "list":
            em = Embed(title="Contest List", description="List of available contests.", color=BOT_COLOUR)
            for x in contest_list:
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
            'help': Language.help,
            'list': Language.list,
            'change': Language.change,
            'current': Language.current,
        }
        info = {
            'bot' : bot,
            'channel' : message.channel,
            'user' : user,
            'content' : content,
        }
        await call[second_command](info)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX):].strip().split(" ")
        command = stripped_message[0]
        await process_command(bot.send_message, message, command, stripped_message[1:])

#token = ""

try:
    bot.loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    for x in users.values():
        x.save()
    for x in contest_list:
        x.save()
    for x in problem_list:
        x.save()
    judge.stop()
finally:
    bot.loop.close()
