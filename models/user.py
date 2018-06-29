import database
import json
import sys
from util import *

class Player:
    def __init__(self,discord_id,points,rank,language,is_admin):
        self.discord_user = database.discord_users_list[str(discord_id)]
        self.points = points
        self.rank = rank
        self.language = language
        self.is_admin = is_admin

    def save(self):
        with open("players/" + self.discord_user.id + ".json", "w") as s:
            s.write(str(self.__dict__).replace(repr(self.__dict__['discord_user']), self.__dict__['discord_user'].id).replace("'","\""))

    @property
    def rank_title(self):
        for x in range(len(ranking_titles)-1):
            if ranking_titles[x][0] <= self.rank < ranking_titles[x+1][0]:
                return ranking_titles[x][1]
        return None

    def __repr__(self):
        return self.discord_user.id

    def __str__(self):
        return "ID: {}, Points: {}, Rank: {}".format(self.discord_user.id,self.points,self.rank)

    def __eq__(self, other):
        return self.discord_user.id == other.discord_user.id

    @staticmethod
    def read(discord_id):
        try:
            with open("players/{}.json".format(discord_id),"r") as f:
                d = json.loads(f.read())
            return Player(d["discord_user"],d["points"],d["rank"],d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable user file, {}.".format(discord_id), file=sys.stderr)

