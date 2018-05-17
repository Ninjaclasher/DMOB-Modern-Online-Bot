import requests
import time
import asyncio
from threading import Thread

class DMOBGame:
    def __init__(self, bot, channel):
        self.channel = channel
        self.bot = bot
        self.members = []
        self.contest = None
        self.window = 0
        self.start_time = 0
    def reset(self):
        self.start_time = 0
        self.window = 0
        self.contest = None
        self.members = []
    def plural(self, num):
        return "s" if num != 1 else ""
    def to_time(self, secs):
        if secs == 0:
            return ""
        elif secs < 60:
            return str(secs) + " second" + self.plural(secs)
        elif secs < 3600:
            return (str(secs//60) + " minute" + self.plural(secs//60) + " " + self.to_time(secs%60)).strip()
        elif secs < 86400:
            return (str(secs//3600) + " hour" + self.plural(secs//3600) + " " + self.to_time(secs%3600)).strip()
    async def count_down(self):
        announce_time = [43600,21600,7200,3600,1800,600,300,60,30,10,5,-1]
        while announce_time[0] > self.window/2:
            del announce_time[0]
        while time.time()-self.start_time < self.window:
            if self.start_time+self.window-time.time() < announce_time[0]:
                await self.bot.send_message(self.channel, self.to_time(announce_time[0]) + " left!")
                del announce_time[0]
            await asyncio.sleep(1)
        await self.bot.send_message(self.channel, "The contest has ended!")
        await self.rankings()
        self.reset()
    async def check_contest_running(self, message="There is no contest running in this channel! Please start a contest first."):
        if self.start_time == 0:
            await self.bot.send_message(self.channel, message)
            return False
        return True
    async def in_contest(self,user):
        return user in self.members
    
    async def join(self, user):
        if await self.in_contest(user):
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(user)
            await self.bot.send_message(self.channel, "You have joined the contest!")

    async def submit(self, message, user, problem_code, url):
        await self.bot.send_message(self.channel, "Submitting code... please wait")
        file_name = problem_code + "_" + user.discord_id + "_" + str(int(time.time()))
        f = open("submissions/" + file_name, "wb")
        f.write(requests.get(url).content)
        f.close()
        await self.bot.delete_message(message)
        #TODO - Judge the code

    async def start_round(self, contest, window=10800):
        if self.start_time != 0:
            await self.bot.send_message(self.channel, "There is already a contest runnning in this channel. Please wait until the contest is over.")
            return
        self.contest = contest
        self.start_time = time.time()
        self.window = window
        await self.bot.send_message(self.channel, "A contest has started!")
        await self.bot.loop.create_task(self.count_down())

    async def display_problem(self, user, problem_code):
        discord_user = await self.bot.get_user_info(user.discord_id)
        for x in self.contest.problems:
            if x.problem_code == problem_code:
                await self.bot.send_file(discord_user, x.file)
                await self.bot.send_message(self.channel, discord_user.mention + ", problem statement has been sent to your private messages.")
                return True
        await self.bot.send_message(self.channel, "```\nThe problems in this contest are:\n" + "\n".join(x.problem_code for x in self.contest.problems) + "\n```")
        return False

    async def rankings(self):
        await self.bot.send_message(self.channel, "The current rankings are: ")
        #TODO
        await self.bot.send_message(self.channel, "UNIMPLEMENTED")
    async def end_round(self):
        self.reset()
        
