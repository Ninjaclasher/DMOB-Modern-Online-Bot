import sys
import os

from discord import *
from DMOBGame import *
from models import Player
from settings import *
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
    await database.load(bot)
    print("Database loaded.")

async def process_command(message, command, content):
    try:
        game = database.games[message.channel]
    except KeyError:
        game = database.games[message.channel] = DMOBGame(bot, message.channel)
    try:
        user = database.users[message.author.id]
    except KeyError:
        database.discord_users_list[message.author.id] = await bot.get_user_info(message.author.id)
        user = database.users[message.author.id] = Player(message.author.id,0,0,DEFAULT_LANG,0)
    
    if command in help_list.keys():
        try:
            second_command = content[0].lower()
            del content[0]
        except IndexError:
            await bot.send_message(message.channel, "Please enter a subcommand.")
            return
    else:
        second_command = ""
    info = {
        'bot'    : bot,
        'channel': message.channel,
        'user'   : user,
        'content': content,
        'message': message,
    }
    
    #No code injection for you
    if "__" in second_command:
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
        info['game'] = game
        if second_command in requires_contest_running and not await game.check_contest_running():
            return
        elif second_command in requires_in_contest and not await game.in_contest(user): 
            await bot.send_message(message.channel, "You are not in this contest! Please join first.")
            return
    if command in help_list.keys():
        try:
            call = getattr(handlers, command.capitalize())
            await getattr(call, second_command)(info)
        except AttributeError:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.type == MessageType.default and message.content.startswith(COMMAND_PREFIX):
        stripped_message = message.content[len(COMMAND_PREFIX):].strip().split(" ")
        command = stripped_message[0]
        await process_command(message, command, stripped_message[1:])

try:
    bot.loop.run_until_complete(bot.start(DMOBToken))
except KeyboardInterrupt:
    bot.loop.run_until_complete(bot.logout())
    bot.loop.run_until_complete(database.save())
finally:
    bot.loop.close()
