import math
import sys
import os
import random
import threading

from bridge import JudgeHandler, JudgeServer
from discord import *
from DMOBGame import *
from handlers import *
from models import Contest, Problem, Player, Submission
from settings import *
from sortedcontainers import SortedSet
from util import *

import database

bot = Client()
judge = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    threading.Thread(target=judge.serve_forever).start()
    await database.load(bot)

async def process_command(message, command, content):
    try:
        game = database.games[message.channel]
    except KeyError:
        game = database.games[message.channel] = DMOBGame(bot, message.channel, judge)
    try:
        user = database.users[message.author.id]
    except KeyError:
        user = database.users[message.author.id] = Player(message.author.id,0,0,DEFAULT_LANG,0)

    if command in help_list.keys():
        try:
            second_command = content[0].lower()
            del content[0]
        except IndexError:
            await bot.send_message(message.channel, "Please enter a subcommand.")
            return

    if command == "help":
        em = Embed(title="Help",description="Available commands from DMOB", color=BOT_COLOUR)
        for key, value in help_list[""].items():
            em.add_field(name=COMMAND_PREFIX + key, value=value)
        await bot.send_message(message.channel,embed=em)
        return
    elif command == "contest":
        requires_contest_running = ["join", "rankings", "info", "end", "submit", "problem"]
        requires_in_contest = ["submit", "problem"]
        call = {
            'help'    : Contests.help,
            'list'    : Contests.list,
            'start'   : Contests.start,
            'join'    : Contests.join,
            'rankings': Contests.rankings,
            'info'    : Contests.info,
            'end'     : Contests.end,
            'submit'  : Contests.submit,
            'problem' : Contests.problem,
        }
        info = {
            'bot'    : bot,
            'channel': message.channel,
            'user'   : user,
            'content': content,
            'message': message,
            'game'   : game,
        }
        if second_command in requires_contest_running and not await game.check_contest_running():
            return
        elif second_command in requires_in_contest and not await game.in_contest(user): 
            await bot.send_message(message.channel, "You are not in this contest! Please join first.")
            return
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
    elif command == "submissions":
        call = {
            'help'   : Submissions.help,
            'list'   : Submissions.list,
            'view'   : Submissions.view,
            'code'   : Submissions.code,
            'delete' : Submissions.delete,
        }
        info = {
            'bot'    : bot,
            'channel': message.channel,
            'user'   : user,
            'content': content,
        }
    if command not in help_list.keys():
        return
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
        await process_command(message, command, stripped_message[1:])

token = DMOBToken

try:
    bot.loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    database.save()
    judge.stop()
finally:
    bot.loop.close()
