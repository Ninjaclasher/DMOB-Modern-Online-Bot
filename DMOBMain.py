import math
import sys
import os
import random

from Contest import *
from discord import *
from DMOBGame import *
from DMOBPlayer import *
from Problem import *

COMMAND_PREFIX = "&"
help_list = {
    "help": "This command",
    "contest (subcommand)": "Manages a contest. Type `" + COMMAND_PREFIX + "contest help` for subcommands.",
    "language (subcommand)": "Manages your preferred language settings. Type `" + COMMAND_PREFIX + "language help` for subcommands.",
}
contest_help_list = {
    "help": "Displays this message.",
    "start [time window]": "Starts a contest for the specified amount of time. Defaults to 3 hours.",
    "end": "Ends the contest.",
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
        em = Embed(title="Help",description="Available commands from DMOB", colour=0x4286F4)
        for key, value in help_list.items():
            em.add_field(name=COMMAND_PREFIX + key, value=value)
        await bot.send_message(message.channel,embed=em)
    elif command == "contest":
        if second_command == "help":
            em = Embed(title="Contest Help",description="Available Contest commands from DMOB", color=0x4286F4)
            for key, value in contest_help_list.items():
                em.add_field(name=COMMAND_PREFIX + "contest " + key, value=value)
            await bot.send_message(message.channel,embed=em)
            return
        elif second_command == "start":
            try:
                if int(content[0]) < 1 or int(content[0]) > 31536000:
                    raise ValueError
                await game.start_round(contest_list[0], int(content[0]))
            except (IndexError, ValueError):
                await game.start_round(contest_list[0])
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
                await game.submit(message, user, content[0], message.attachments[0]["url"])
        elif second_command == "problem":
            await game.display_problem(user, content[0].strip().lower() if len(content) > 0 else " ")
    elif command == "language":
        if second_command == "help":
            em = Embed(title="Language Help",description="Available Language commands from DMOB", color=0x4286F4)
            for key, value in language_help_list.items():
                em.add_field(name=COMMAND_PREFIX + "language " + key, value=value)
            await bot.send_message(message.channel, embed=em)
        elif second_command == "list":
            await bot.send_message(message.channel, "Available languages are `" + " ".join(languages) + "`")
        elif second_command == "change":
            try:
                lang = content[0].lower()
                if not lang in languages:
                    raise IndexError
                user.language = lang
                await bot.send_message(message.channel, "Your language has been changed to`" + lang + '`')
            except IndexError:
                await bot.send_message(message.channel, "Please enter a valid language.")
        elif second_command == "current":
            await bot.send_message(message.channel, "Your current language is `" + user.language + "`")


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
finally:
    bot.loop.close()
