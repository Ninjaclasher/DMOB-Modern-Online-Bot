import database
import json
import sys
from bisect import bisect
from util import *

class Player:
    def __init__(self,discord_id,points=0,rank=[],volatility=385,language=DEFAULT_LANG,is_admin=0):
        self.discord_user = database.discord_users_list[str(discord_id)]
        self.points = points
        self.rank = rank
        self.volatility = volatility
        self.language = language
        self.is_admin = is_admin

    def save(self):
        with open("players/" + self.discord_user.id + ".json", "w") as s:
            s.write(str(self.__dict__).replace(repr(self.__dict__['discord_user']), self.__dict__['discord_user'].id).replace("'","\""))

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

    def __repr__(self):
        return self.discord_user.id

    def __eq__(self, other):
        return self.discord_user.id == other.discord_user.id

    @staticmethod
    def read(discord_id):
        try:
            with open("players/{}.json".format(discord_id),"r") as f:
                d = json.loads(f.read())
            return Player(d["discord_user"],d["points"],d["rank"],d["volatility"], d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable user file, {}.".format(discord_id), file=sys.stderr)

