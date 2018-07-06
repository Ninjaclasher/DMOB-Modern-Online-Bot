import asyncio
import datetime
import os
import requests
import time
import threading

from discord import *
from models import Problem, ContestPlayer, Submission, Rank
from settings import *
from util import *

import database
import handlers

# ------------- dmob_game ------------------------------
# channel | contest | window | start_time | contest_state
#
# contest_state 
# 0 = before_start
# 1 = running
# 2 = contest over
# 3 = contest finished

# --------dmob_game_participation--------
#              user | dmob_game

class DMOBGame:
    def __init__(self, bot, id, channel, contest="", start_time=datetime.datetime.now(), window=10800, contest_state=0):
        self.bot = bot
        
        self.id = id
        self._channel = channel
        self._contest = contest
        self.contest = database.get_contests(deleted_contests=True, id=self._contest)[0]
        self.start_time = start_time
        self.window = window
        self.contest_state = contest_state
        
        self.running_submissions = set()
        self.members = []

    def __repr__(self):
        return str(self._channel)

    def db_save(self):
        return self.id, self._channel, self._contest, self.start_time, self.window, self.contest_state
    
    @property
    def channel(self):
        return database.discord_channels_list[self._channel]

    @property
    def contest_running(self):
        return self.contest_state == 1
    
    @property
    def contest_pending_submissions(self):
        return self.contest_state == 2

    @property
    def contest_over(self):
        return self.contest_state == 3

    def update_ratings(self):
        self.update_score()
        rated_members = self.members
        old_rating = [x.user.rating for x in rated_members]
        old_volatility = [x.user.volatility for x in rated_members]
        actual_rank = list(range(1,len(rated_members)+1))
        times_rated = [len(x.user.rank) for x in rated_members]
        new_rating, new_volatility = recalculate_ratings(old_rating, old_volatility, actual_rank, times_rated)
        for x in range(len(rated_members)):
            database.add_rank(Rank(None, rated_members[x].user.id, new_rating[x], new_volatility[x]))

    def update_score(self):
        self.members.sort(key=lambda x: x.total_score,reverse=True)
    
    def update_state(self, state):
        self.contest_state = state
        database.update_game_state(self)

    async def on_start_submission(self, id):
        self.running_submissions.add(id)

    async def on_finish_submission(self, sub):
        msg = "{0}, you received a score of {1} for your submission to `{2}`. Details on your submission have been PM'd to you."
        await self.bot.send_message(self.channel, msg.format(sub.user.discord_user.mention, sub.score, sub.problem.code))
        get_element(self.members, ContestPlayer(sub.user)).update_best()
        self.update_score()
        self.running_submissions.remove(sub.submission_id)
    
    async def count_down(self):
        self.update_state(1)
        announce_time = [1209600,604800,86400,43600,21600,7200,3600,1800,600,300,60,30,10,5,-1]
        while announce_time[0] > self.window/2:
            del announce_time[0]
        while (datetime.datetime.now()-self.start_time).total_seconds() < self.window:
            if (self.start_time-datetime.datetime.now()).total_seconds() < announce_time[0]-self.window:
                await self.bot.send_message(self.channel, "{} left!".format(to_time(announce_time[0])))
                del announce_time[0]
            await asyncio.sleep(1)
        await self.bot.send_message(self.channel, "The contest has ended!")
        if len(self.running_submissions) != 0:
            self.update_state(2)
            await self.bot.send_message(self.channel, "Waiting for submissions for finish running...")
            while len(self.running_submissions) != 0:
                await asyncio.sleep(0.5)
        try:
            self.update_ratings()
            await self.rankings()
        except:
            import traceback
            traceback.print_exc()
        self.update_state(3)
        database.update_game_state(self)

    def in_contest(self,user):
        return ContestPlayer(user) in self.members
    
    async def join(self, user):
        if self.in_contest(user):
            await self.bot.send_message(self.channel, "You are already in the contest!")
        else:
            self.members.append(ContestPlayer(user, self))
            await self.bot.send_message(self.channel, "You have joined the contest!")

    async def start_round(self, user):
        await self.bot.send_message(self.channel, "{} started a contest for {}!".format(user.discord_user.mention, to_time(self.window)))
        await self.bot.loop.create_task(self.count_down())
    
    async def display_problem(self, user, problem_code):
        if Problem(None, problem_code) in self.contest.problems:
            info = {
                'bot'        : self.bot,
                'channel'    : self.channel,
                'user'       : user,
                'content'    : [problem_code],
                'description': "Details on problem `{0}` in the `{1}` contest".format(problem_code, self.contest.name),
            }
            await handlers.Problem().view(info,in_contest=True)
        else:
            em = Embed(title="Problems List", description="Problems in the `{}` contest.".format(self.contest.name), color=BOT_COLOUR)
            em.add_field(name="Problem Number", value="\n".join(map(str,range(1,len(self.contest.problems)+1))))
            em.add_field(name="Problem Code", value="\n".join(x.code for x in self.contest.problems))
            em.add_field(name="Problem Name", value="\n".join(x.name for x in self.contest.problems))
            await self.bot.send_message(self.channel, embed=em)
    
    async def rankings(self):
        em = Embed(title="Rankings",description="The current rankings for this contest.", color=BOT_COLOUR)
        if len(self.members) != 0:
            names = "\n".join(str(x.user.discord_user)[:20] for x in self.members)
            em.add_field(name="Name", value=names)
            curvalue = "\n".join("`{}`".format(" ".join("{:3s}".format(str(int(z))) for z in y.best_submissions)) for y in self.members)
            em.add_field(name="Problem Scores", value=curvalue)
            score_sum = "\n".join(str(sum(y.best_submissions)) for y in self.members)
            em.add_field(name="Total", value=score_sum)
        else:
            em.add_field(name="The contest is empty", value="No one has joined the contest yet.")
        await self.bot.send_message(self.channel,embed=em)

    async def info(self):
        em = Embed(title="Info",description="Information on this contest.", color=BOT_COLOUR)
        em.add_field(name="Contest Name", value=self.contest.name)
        em.add_field(name="Number of Users", value=str(len(self.members)))
        time_left = self.window - (datetime.datetime.now()-self.start_time).total_seconds()
        em.add_field(name="Time Left", value=to_time(int(time_left)))
        await self.bot.send_message(self.channel,embed=em)

    async def end_round(self):
        self.window = 0
