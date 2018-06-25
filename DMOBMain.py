import math
import sys
import os
import random
import threading

from bridge import JudgeHandler, JudgeServer
from discord import *
from DMOBGame import *
from models import Contest, Problem, Player, Submission
from settings import *
from sortedcontainers import SortedSet
from util import *

import database
import handlers

bot = Client()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    database.judgeserver = JudgeServer(BRIDGED_IP_ADDRESS, JudgeHandler)
    await database.load(bot)
    threading.Thread(target=database.judgeserver.serve_forever).start()

async def process_command(message, command, content):
    try:
        game = database.games[message.channel]
    except KeyError:
        game = database.games[message.channel] = DMOBGame(bot, message.channel)
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

    info = {
        'bot'    : bot,
        'channel': message.channel,
        'user'   : user,
        'content': content,
        'message': message,
    }

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
            'help'    : handlers.Contest.help,
            'list'    : handlers.Contest.list,
            'start'   : handlers.Contest.start,
            'join'    : handlers.Contest.join,
            'rankings': handlers.Contest.rankings,
            'info'    : handlers.Contest.info,
            'end'     : handlers.Contest.end,
            'submit'  : handlers.Contest.submit,
            'problem' : handlers.Contest.problem,
        }
        info['game'] = game
        if second_command in requires_contest_running and not await game.check_contest_running():
            return
        elif second_command in requires_in_contest and not await game.in_contest(user): 
            await bot.send_message(message.channel, "You are not in this contest! Please join first.")
            return
    elif command == "problem":
        call = {
            'help'   : handlers.Problem.help,
            'list'   : handlers.Problem.list,
            'view'   : handlers.Problem.view,
            'add'    : handlers.Problem.add,
            'make'   : handlers.Problem.make,
            'change' : handlers.Problem.change,
            'delete' : handlers.Problem.delete,
        }
    elif command == "language":
        call = {
            'help'   : handlers.Language.help,
            'list'   : handlers.Language.list,
            'change' : handlers.Language.change,
            'current': handlers.Language.current,
        }
    elif command == "submissions":
        call = {
            'help'   : handlers.Submissions.help,
            'list'   : handlers.Submissions.list,
            'view'   : handlers.Submissions.view,
            'code'   : handlers.Submissions.code,
            'delete' : handlers.Submissions.delete,
        }
    elif command == "judge":
        call = {
            'help'   : handlers.Judge.help,
            'list'   : handlers.Judge.list,
            'view'   : handlers.Judge.view,
            'add'    : handlers.Judge.add,
            'delete' : handlers.Judge.delete,
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
    database.judgeserver.stop()
finally:
    bot.loop.close()
