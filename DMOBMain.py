import math
import sys
import os
import random
#import util

from discord import *
from DMOBGame import *

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
        game = games[message.channel] = DMOBGame(send, message.channel)
    if command == "":
        pass

COMMAND_PREFIX = "&"

@bot.event
async def on_message(message):
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX)].strip()
        command = stripped_message.split(" ")[0]
        await process_command(bot.send_message, message, command, stripped_message[1:])

bot.run("token")
