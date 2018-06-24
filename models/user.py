import json
import lists
import sys

class Player:
    def __init__(self,discord_id,points,rank,language,is_admin):
        self.discord_user = lists.discord_users_list[str(discord_id)]
        self.points = points
        self.rank = rank
        self.language = language
        self.is_admin = is_admin

    def save(self):
        s = open("players/" + self.discord_user.id + ".json", "w")
        s.write(str(self.__dict__).replace(repr(self.__dict__['discord_user']), self.__dict__['discord_user'].id).replace("'","\""))
        s.close()

    def __repr__(self):
        return self.discord_user.id

    def __str__(self):
        return "ID: {}, Points: {}, Rank: {}".format(self.discord_user.id,self.points,self.rank)

    def __eq__(self, other):
        return self.discord_user.id == other.discord_user.id

    @staticmethod
    def read(discord_id):
        try:
            f = open("players/" + discord_id + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Player(d["discord_user"],d["points"],d["rank"],d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable user file, " + str(discord_id) + ".", file=sys.stderr)

