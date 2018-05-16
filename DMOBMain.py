import math
import sys
import os
import random

from discord import *
from DMOBGame import *
from Problem import *
from DMOBPlayer import *
from Contest import *

help_list = {
    "help": "This command",
    "contest": "Manages a contest. Subcommands {start, end, submit, problem, join, rankings}",
    "language": "Manages your preferred language. Subcommands {list, change, current}",
}
languages = ["cpp", "java8", "turing", "python2", "python3", "pypy2", "pypy3"]
two_commands = ["contest", "language"]
contest_list = [Contest.read(x.split(".")[0]) for x in os.listdir("contests") if x.split(".")[1] == "json"]
problem_list = [Problem.read(x.split(".")[0]) for x in os.listdir("problems") if x.split(".")[1] == "json"]
users = {}
for x in os.listdir("players"):
    x = x.split(".")
    if x[1] == "json":
        users[x[0]] = DMOBPlayer.read(x[0])

bot = Client()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

games = {}

async def process_command(send, message, command, content):
    try:
        game = games[message.channel]
    except KeyError:
        game = games[message.channel] = DMOBGame(bot, message.channel)
    try:
        user = users[message.author.id]
    except KeyError:
        user = users[message.author.id] = DMOBPlayer(message.author.id,0,0,"cpp",0)
    if command in two_commands:
        try:
            second_command = content[0].lower()
            del content[0]
        except IndexError:
            await bot.send_message(message.channel, "Please enter a subcommand.")
            return
    if command == "help":
        msg = ["```","Available commands from DMOB:"]
        for key, value in help_list.items():
            msg.append(key + " - " + value)
        msg.append("```")
        await bot.send_message(message.channel, "\n".join(msg))
    elif command == "contest":
        if second_command == "start":
            try:
                await game.start_round(contest_list[0], int(content[0]))
            except (IndexError, ValueError):
                await game.start_round(contest_list[0])
        elif second_command == "end":
            await game.end_round()
        elif second_command == "submit":
            if len(message.attachments) != 1:
                await bot.send_message(message.channel, "Please upload one file for judging.")
            if len(message.content) != 1:
                await bot.send_message(message.channel, "Please select a problem to submit the code to.")
            await game.submit(user, message.content[0], message.attachmenst[0])
        elif second_command == "problem":
            if not await game.check_contest_running():
                return
            if len(content) != 1 or not await game.display_problem(user, content[0].strip().lower()):
                await bot.send_message(message.channel, "Please enter a valid problem code.")
        elif second_command == "join":
            await game.join(user)
        elif second_command == "rankings":
            await game.rankings()
    elif command == "language":
        if second_command == "list":
            await bot.send_message(message.channel, "Available languages are `" + " ".join(languages) + "`")
        elif second_command == "change":
            try:
                lang = content[0].lower()
                if not lang in languages:
                    raise IndexError
                user.language = lang
                await bot.send_message(message.channel, "Your language has been changed to " + lang)
            except IndexError:
                await bot.send_message(message.channel, "Please enter a valid language.")
        elif second_command == "current":
            await bot.send_message(message.channel, "Your current language is `" + user.language + "`")

COMMAND_PREFIX = "&"

@bot.event
async def on_message(message):
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX):].strip().split(" ")
        command = stripped_message[0]
        await process_command(bot.send_message, message, command, stripped_message[1:])

token = ""

try:
    bot.loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    for x in users.values():
        x.save()
finally:
    bot.loop.close()
