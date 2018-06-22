import asyncio
import os
import requests
import time
import threading

from models import Problem, ContestPlayer
from discord import *
from util import *

class DMOBGame:
    def __init__(self, bot, channel, judge):
        self.channel = channel
        self.bot = bot
        self.judge = judge
        self.members = []
        self.contest = None
        self.window = 0
        self.start_time = 0
    def reset(self):
        self.start_time = 0
        self.window = 0
        self.members = []
        self.contest = None
    async def count_down(self):
        announce_time = [1209600,604800,86400,43600,21600,7200,3600,1800,600,300,60,30,10,5,-1]
        while announce_time[0] > self.window/2:
            del announce_time[0]
        while time.time()-self.start_time < self.window:
            if self.start_time+self.window-time.time() < announce_time[0]:
                await self.bot.send_message(self.channel, to_time(announce_time[0]) + " left!")
                del announce_time[0]
            await asyncio.sleep(1)
        await self.bot.send_message(self.channel, "The contest has ended!")
        await self.rankings()
        self.reset()
    async def wait_submission_finish(self, id, user_idx, problem_idx, problem, submission_time):
        while True:
            try:
                sub = self.judge.judges.finished_submissions[id]
                print(str(sub))
                score = int(sub.points/float(sub.total)*100) if sub.total > 0 else 0
                await self.bot.send_message(self.channel, self.members[user_idx].discord_user.mention + ", you received a score of " + str(score) + " for your submission to `" + problem.problem_code + "`. Details on your submission have been PM'd to you.")
                em = Embed(title="Submission Details", description="Details on your submission to `" + problem.problem_code + "` in the " + self.contest.name + " contest.", color=BOT_COLOUR)
                em.add_field(name="Problem Name", value=problem.problem_name)
                em.add_field(name="Submission ID", value=str(sub.submission_id))
                em.add_field(name="Verdict", value=sub.result + " (" + verdicts[sub.result] + ")")
                em.add_field(name="Points Recieved", value=str(score))
                em.add_field(name="Total Running Time", value=str(round(sub.time,2)) + "s")
                em.add_field(name="Memory Usage", value=to_memory(sub.memory))
                await self.bot.send_message(self.members[user_idx].discord_user, embed=em)
                if score > self.members[user_idx].problems[problem_idx]:
                    self.members[user_idx].time[problem_idx] = submission_time-self.start_time
                    self.members[user_idx].problems[problem_idx] = score
                break
            except KeyError:
                pass
            await asyncio.sleep(0.5)
    async def check_contest_running(self, message="There is no contest running in this channel! Please start a contest first."):
        if self.start_time == 0:
            await self.bot.send_message(self.channel, message)
            return False
        return True
    async def in_contest(self,user):
        return ContestPlayer(user,None,0) in self.members
    
    async def join(self, user):
        if await self.in_contest(user):
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(ContestPlayer(user,await self.bot.get_user_info(user.discord_id),len(self.contest.problems)))
            await self.bot.send_message(self.channel, "You have joined the contest!")

    async def submit(self, message, user, problem_code, url, id):
        p = -1
        submission_time = time.time()
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
        problem = Problem.read(problem_code)
        self.judge.judges.judge(id, problem_code, problem.time, problem.memory, judge_lang[user.language], open("submissions/" + file_name, "r").read())
        await self.bot.loop.create_task(self.wait_submission_finish(id, self.members.index(ContestPlayer(user,None,0)), p, problem, submission_time))

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
                em = Embed(title="Problem Info", description="`" + problem_code + "` problem info.")
                em.add_field(name="Problem Name", value=x.problem_name)
                em.add_field(name="Problem Code", value=x.problem_code)
                em.add_field(name="Time Limit", value=str(x.time) + "s")
                em.add_field(name="Memory Limit", value=to_memory(x.memory))
                await self.bot.send_message(discord_user, embed=em)
                await self.bot.send_file(discord_user, x.file)
                await self.bot.send_message(self.channel, discord_user.mention + ", problem statement has been sent to your private messages.")
                return True
        em = Embed(title="Problems List", description="Problems in the " + self.contest.name + " contest.", color=BOT_COLOUR)
        em.add_field(name="Problem Number", value="\n".join(map(str,range(1,len(self.contest.problems)+1))))
        em.add_field(name="Problem Code", value="\n".join(x.problem_code for x in self.contest.problems))
        em.add_field(name="Problem Name", value="\n".join(x.problem_name for x in self.contest.problems))
        await self.bot.send_message(self.channel, embed=em)
        return False
    
    async def rankings(self):
        self.members.sort(key=lambda x: [sum(x.problems), -sum(x.time)],reverse=True)
        em = Embed(title="Rankings",description="The current rankings for this contest.", color=BOT_COLOUR)
        if len(self.members) != 0:
            names = "\n".join([str(x.discord_user)[:20] for x in self.members])
            em.add_field(name="Name", value=names)
            curvalue = "\n".join("`"+"".join("{:5s}".format(str(z)) for z in y.problems)+"`" for y in self.members)
            em.add_field(name="Problem Scores", value=curvalue)
            score_sum = "\n".join(str(sum(y.problems)) for y in self.members)
            em.add_field(name="Total", value=score_sum)
        else:
            em.add_field(name="The contest is empty", value="No one has joined the contest yet.")
        await self.bot.send_message(self.channel,embed=em)

    async def info(self):
        em = Embed(title="Info",description="Information on this contest.", color=BOT_COLOUR)
        em.add_field(name="Contest Name", value=self.contest.name)
        em.add_field(name="Number of Users", value=str(len(self.members)))
        em.add_field(name="Time Left", value=to_time(int(self.start_time+self.window-time.time())))
        await self.bot.send_message(self.channel,embed=em)

    async def end_round(self):
       self.window = 0 
