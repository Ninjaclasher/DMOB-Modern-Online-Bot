import math
import sys
import os
import random

from discord import *
from DMOBGame import *
from DMOBPlayer import *
from util import *

bot = Client()

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

games = {}
users = {}

async def process_command(send, message, command, content):
    try:
        game = games[message.channel]
    except KeyError:
        game = games[message.channel] = DMOBGame(send, message.channel)
    try:
        user = users[message.author.id]
    except KeyError:
        user = users[message.author.id] = DMOBPlayer(message.author.id,0,0,"cpp")
    if command == "help":
        pass
    elif command == "start":
        await game.start_round()
    elif command == "end":
        await game.end_round()
    elif command == "submit":
        pass
    elif command == "problem":
        pass
    elif command == "join":
        pass
    elif command == "language":
        if len(content) == 0:
            return
        second_command = content[0].lower()
        del content[0]
        if second_command == "list":
            await bot.send_message(message.channel, "Available languages are " + " ".join(languages))
        elif second_command == "change":
            try:
                lang = content[0].lower()
                if not lang in languages:
                    raise IndexError
                user.language = lang
                await bot.send_message(message.channel, "Your language has been changed to " + lang)
            except IndexError:
                await bot.send_message(message.channel, "Please enter a valid langauge.")
        elif second_command == "current":
            await bot.send_message(message.channel, "Your current language is " + user.language)
    elif command == "rankings":
        pass

COMMAND_PREFIX = "&"

@bot.event
async def on_message(message):
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX):].strip().split(" ")
        command = stripped_message[0]
        await process_command(bot.send_message, message, command, stripped_message[1:])

bot.run("NDQ1NzUxNzUyNjEyOTA0OTYw.DdvC5g.m-Ac3YunaEF5gGu4WhU0Y9Xh4es")
