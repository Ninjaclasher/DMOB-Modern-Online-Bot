import database
import database
import json
import sys
from bisect import bisect
from collections import defaultdict
from sortedcontainers import SortedSet
from util import *

class Player:
    def __init__(self,discord_id,points=0,rank=[],volatility=385,_submissions=[],language=DEFAULT_LANG,is_admin=0):
        self.discord_user = database.discord_users_list[str(discord_id)]
        self.points = points
        self.rank = rank
        self.volatility = volatility
        self._submissions = SortedSet(_submissions)
        self.language = language
        self.is_admin = is_admin

    def __repr__(self):
        return self.discord_user.id

    def __eq__(self, other):
        return self.discord_user.id == other.discord_user.id
 
    async def update_points(self):
        with await database.locks["user"][self.discord_user.id]:
            max_subs = defaultdict(lambda: 0.0)
            for x in self.submissions:
                max_subs[x.problem.problem_code] = max(max_subs[x.problem.problem_code], x.points/x.total*x.problem.point_value)
            self.points = sum(max_subs.values())

    async def save(self):
        with await database.locks["user"][self.discord_user.id]:
            self._submissions = list(self._submissions)
            self.discord_user = self.discord_user.id
            with open("players/" + self.discord_user + ".json", "w") as s:
                s.write(str(self.__dict__).replace("'","\""))
            self.discord_user = database.discord_users_list[self.discord_user]
            self._submissions = SortedSet(self._submissions)

    @property
    def rating(self):
        return 1200 if not self.rated else self.rank[-1]

    @property
    def rank_title(self):
        if not self.rated:
            return RANKING_TITLES[0]
        return RANKING_TITLES[bisect(RANKING_VALUES, self.rank[-1])-1]
    
    @property
    def rank_colour(self):
        if not self.rated:
            return RANKING_COLOUR[0]
        return RANKING_COLOUR[bisect(RANKING_VALUES, self.rank[-1])-1]
            
    @property
    def rated(self):
        return len(self.rank) > 0

    @property
    def submissions(self):
        return [x for x in database.submission_list if x.submission_id in self._submissions]

    @staticmethod
    def read(discord_id):
        try:
            with open("players/{}.json".format(discord_id),"r") as f:
                d = json.loads(f.read())
            return Player(d["discord_user"],d["points"],d["rank"],d["volatility"],d["_submissions"],d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable user file, {}.".format(discord_id), file=sys.stderr)

