import asyncio
import requests
import time

from ContestPlayer import *
from discord import *

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
        self.members = []
        self.contest = None
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
        elif secs < 604800:
            return(str(srcs//86400) + " day" + self.plural(secs//86400) + " " + self.to_time(secs%86400)).strip()
    async def count_down(self):
        announce_time = [86400,43600,21600,7200,3600,1800,600,300,60,30,10,5,-1]
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
        return ContestPlayer(user,0) in self.members
    
    async def join(self, user):
        if await self.in_contest(user):
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(ContestPlayer(user,len(self.contest.problems)))
            await self.bot.send_message(self.channel, "You have joined the contest!")

    async def submit(self, message, user, problem_code, url):
        p = -1
        u = self.members.index(ContestPlayer(user,0))
        for i in range(len(self.contest.problems)):
            if self.contest.problems[i].problem_code == problem_code:
                p = i
                break
        if p != -1:
            await self.bot.send_message(self.channel, "Submitting code... please wait")
            file_name = problem_code + "_" + user.discord_id + "_" + str(int(time.time()))
            f = open("submissions/" + file_name, "wb")
            f.write(requests.get(url).content)
            f.close()
        await self.bot.delete_message(message)
        if p == -1:
            await self.bot.send_message(self.channel, "Invalid problem code, `" + problem_code + '`')
            return
        #TODO - Judge the code
        score = __import__("random").randint(0,100)
        discord_user = await self.bot.get_user_info(user.discord_id)
        await self.bot.send_message(self.channel, discord_user.mention + ", you received a score of " + str(score) + " for your submission to `" + problem_code + "`.")
        if score > self.members[u].problems[p]:
            self.members[u].problems[p] = score
            
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
        em = Embed(title="Problems List", description="Problems in the " + self.contest.name + " contest.", colour=0x4286F4)
        em.add_field(name="Problem Number", value="\n".join(map(str,range(1,len(self.contest.problems)+1))))
        em.add_field(name="Problem Code", value="\n".join(x.problem_code for x in self.contest.problems))
        em.add_field(name="Problem Name", value="\n".join(x.problem_name for x in self.contest.problems))
        await self.bot.send_message(self.channel, embed=em)
        return False
    
    async def rankings(self):
        self.members.sort(key=lambda x: sum(x.problems),reverse=True)
        em = Embed(title="Rankings",description="The current rankings for this contest.", colour=0x4286F4)
        if len(self.members) != 0:
            names = [str(await self.bot.get_user_info(x.user.discord_id))[:20] for x in self.members]
            em.add_field(name="Name", value="\n".join(names))
            for x in range(len(self.contest.problems)):
                values = [str(y.problems[x]) for y in self.members]
                em.add_field(name="Problem " + str(x+1), value="\n".join(values))
            score_sum = [str(sum(y.problems)) for y in self.members]
            em.add_field(name="Total", value="\n".join(score_sum))
        else:
            em.add_field(name="The contest is empty", value="No one has joined the contest yet.")
        await self.bot.send_message(self.channel,embed=em)

    async def info(self):
        em = Embed(title="Info",description="Information on this contest.", color=0x4286F4)
        em.add_field(name="Contest Name", value=self.contest.name)
        em.add_field(name="Number of Competitors", value=str(len(self.members)))
        em.add_field(name="Time Left", value=self.to_time(int(self.start_time+self.window-time.time())))
        await self.bot.send_message(self.channel,embed=em)

    async def end_round(self):
        self.reset()
        
