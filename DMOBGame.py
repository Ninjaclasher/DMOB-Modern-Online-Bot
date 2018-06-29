import asyncio
import os
import requests
import time
import threading

from discord import *
from models import Problem, ContestPlayer, ContestSubmission, Submission
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
        self.running_submissions = set()
        self.window = 0
        self.start_time = 0

    def __repr__(self):
        return self.channel.id

    @property
    def contest_over(self):
        return self.start_time+self.window+0.9 < time.time()
    
    def reset(self):
        self.start_time = 0
        self.window = 0
        self.members = []
        self.contest = None

    def update_ratings(self):
        pass

    def update_score(self):
        self.members.sort(key=lambda x: x.total_score,reverse=True)

    async def count_down(self):
        announce_time = [1209600,604800,86400,43600,21600,7200,3600,1800,600,300,60,30,10,5,-1]
        while announce_time[0] > self.window/2:
            del announce_time[0]
        while time.time()-self.start_time < self.window:
            if self.start_time+self.window-time.time() < announce_time[0]:
                await self.bot.send_message(self.channel, "{} left!".format(to_time(announce_time[0])))
                del announce_time[0]
            await asyncio.sleep(1)
        await self.bot.send_message(self.channel, "The contest has ended!")
        if len(self.running_submissions) != 0:
            await self.bot.send_message(self.channel, "Waiting for submissions for finish running...")
            while len(self.running_submissions) != 0:
                await asyncio.sleep(0.5)
        await self.rankings()
        self.reset()

    async def wait_submission_finish(self, id, author, problem_idx, problem_code, submission_time):
        await self.bot.send_message(self.channel, "{0}, submitting code to `{1}`... please wait.".format(author.user.discord_user.mention, problem_code))
        while True:
            try:
                sub = ContestSubmission(self, *database.judgeserver.judges.finished_submissions[id].__dict__.values())
                database.submission_list.add(sub)
                print(sub)
                info = {
                    'bot'    : self.bot,
                    'channel': author.user.discord_user,
                    'user'   : author.user,
                    'content': [str(id)],
                    'description': "Details on your submission to `{}`".format(problem_code),
                }
                await handlers.Submissions().view(info)
                await self.bot.send_message(self.channel, "{0}, you received a score of {1} for your submission to `{2}`. Details on your submission have been PM'd to you.".format(author.user.discord_user.mention, sub.score, problem_code))
                author.submissions[problem_idx].append(sub)
                self.update_score()
                self.running_submissions.remove(id)
                return
            except KeyError:
                pass
            await asyncio.sleep(0.5)

    async def check_contest_running(self):
        if self.start_time == 0:
            await self.bot.send_message(self.channel, "There is no contest running in this channel! Please start a contest first.")
            return False
        elif self.contest_over:
            await self.bot.send_message(self.channel, "The contest is over! Currently waiting for the last submissions to finish running...")
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
            p = self.contest.problems.index(database.problem_list[problem_code])
            code = requests.get(url).content.decode("utf-8")
        except (ValueError, KeyError):
            await self.bot.send_message(self.channel, "Invalid problem code, `{}`".format(problem_code))
            return
        finally:
            await self.bot.delete_message(message)
        if len(code) > 65536:
            await self.bot.send_message(self.channel, "Please submit a file less than 65536 characters.")
            return
        Submission.save_code(id, code)
        problem = database.problem_list[problem_code]
        self.running_submissions.add(id)
        database.judgeserver.judges.judge(id, problem, judge_lang[user.language], code, user, submission_time)
        await self.bot.loop.create_task(self.wait_submission_finish(id, get_element(self.members, ContestPlayer(user,0)), p, problem_code, submission_time))

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
                'description': "Details on problem `{0}` in the `{1}` contest".format(problem_code, self.contest.name),
                'is_contest' : True,
            }
            await handlers.Problem().view(info)
        else:
            em = Embed(title="Problems List", description="Problems in the `{}` contest.".format(self.contest.name), color=BOT_COLOUR)
            em.add_field(name="Problem Number", value="\n".join(map(str,range(1,len(self.contest.problems)+1))))
            em.add_field(name="Problem Code", value="\n".join(x.problem_code for x in self.contest.problems))
            em.add_field(name="Problem Name", value="\n".join(x.problem_name for x in self.contest.problems))
            await self.bot.send_message(self.channel, embed=em)
    
    async def rankings(self):
        em = Embed(title="Rankings",description="The current rankings for this contest.", color=BOT_COLOUR)
        if len(self.members) != 0:
            names = "\n".join(str(x.user.discord_user)[:20] for x in self.members)
            em.add_field(name="Name", value=names)
            curvalue = "\n".join("`{}`".format(" ".join("{:3s}".format(str(z.score)) for z in y.best_submissions)) for y in self.members)
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
