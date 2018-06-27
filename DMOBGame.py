import asyncio
import os
import requests
import time
import threading


from discord import *
from models import Problem, ContestPlayer, ContestSubmission
from settings import *
from util import *

import database
import handlers

class DMOBGame:
    def __init__(self, bot, channel):
        self.channel = channel
        self.bot = bot
        self.members = []
        self.contest = None
        self.window = 0
        self.start_time = 0

    def __repr__(self):
        return self.channel.id

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

    async def wait_submission_finish(self, id, author, problem_idx, problem, submission_time):
        await self.bot.send_message(self.channel, "Submitting code... please wait")
        while True:
            try:
                sub = ContestSubmission(self, *database.judgeserver.judges.finished_submissions[id].__dict__.values())
                database.submission_list.add(sub)
                print(str(sub))
                info = {
                    'bot'    : self.bot,
                    'channel': author.user.discord_user,
                    'user'   : author.user,
                    'content': [str(id)],
                    'description': "Details on your submission to `" + problem.problem_code + "`",
                }
                await handlers.Submissions.view(info)
                await self.bot.send_message(self.channel, author.user.discord_user.mention + ", you received a score of " + str(sub.score) + " for your submission to `" + problem.problem_code + "`. Details on your submission have been PM'd to you.")
                author.submissions[problem_idx].append(sub)
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
        return ContestPlayer(user,0) in self.members
    
    async def join(self, user):
        if await self.in_contest(user):
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(ContestPlayer(user,len(self.contest.problems)))
            await self.bot.send_message(self.channel, "You have joined the contest!")

    async def submit(self, message, user, problem_code, url, id):
        submission_time = time.time()
        try:
            p = self.contest.problems.index(Problem(problem_code))
            code = requests.get(url).content.decode("utf-8")
        except ValueError:
            await self.bot.send_message(self.channel, "Invalid problem code, `" + problem_code + '`')
            return
        finally:
            await self.bot.delete_message(message)
        if len(code) > 65536:
            await self.bot.send_message(self.channel, "Please submit a file less than 64KB.")
            return
        with open("submissions/" + str(id) + ".code", "w") as f:
            f.write(code)
        problem = database.problem_list[problem_code]
        database.judgeserver.judges.judge(id, problem, judge_lang[user.language], code, user, submission_time)
        await self.bot.loop.create_task(self.wait_submission_finish(id, get_element(self.members, ContestPlayer(user,0)), p, problem, submission_time))

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
        if Problem(problem_code) in self.contest.problems:
            info = {
                'bot'        : self.bot,
                'channel'    : self.channel,
                'user'       : user,
                'content'    : [problem_code],
                'description': "Details on problem `" + problem_code + "` in the `" + self.contest.name + "` contest",
                'is_contest' : True,
            }
            await handlers.Problem.view(info)
        else:
            em = Embed(title="Problems List", description="Problems in the " + self.contest.name + " contest.", color=BOT_COLOUR)
            em.add_field(name="Problem Number", value="\n".join(map(str,range(1,len(self.contest.problems)+1))))
            em.add_field(name="Problem Code", value="\n".join(x.problem_code for x in self.contest.problems))
            em.add_field(name="Problem Name", value="\n".join(x.problem_name for x in self.contest.problems))
            await self.bot.send_message(self.channel, embed=em)
    
    async def rankings(self):
        self.members.sort(key=lambda x: x.total_score,reverse=True)
        em = Embed(title="Rankings",description="The current rankings for this contest.", color=BOT_COLOUR)
        if len(self.members) != 0:
            names = "\n".join([str(x.user.discord_user)[:20] for x in self.members])
            em.add_field(name="Name", value=names)
            curvalue = "\n".join("`"+"".join("{:5s}".format(str(z.score)) for z in y.best_submissions)+"`" for y in self.members)
            em.add_field(name="Problem Scores", value=curvalue)
            score_sum = "\n".join(str(sum(z.score for z in y.best_submissions)) for y in self.members)
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
