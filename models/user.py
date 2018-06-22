import json
import sys

class Player:
    def __init__(self,discord_id,points,rank,language,is_admin):
        self.discord_id = discord_id
        self.points = points
        self.rank = rank
        self.language = language
        self.is_admin = is_admin

    def save(self):
        s = open("players/" + str(self.discord_id) + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __repr__(self):
        return "Player('{}','{}','{}','{}','{}')".format(self.discord_id,self.points,self.rank,self.language,self.is_admin)

    def __str__(self):
        return "ID: {}, Points: {}, Rank: {}".format(self.discord_id,self.points,self.rank)

    def __eq__(self, other):
        return self.discord_id == other.discord_id

    @staticmethod
    def read(discord_id):
        try:
            f = open("players/" + discord_id + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Player(d["discord_id"],d["points"],d["rank"],d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError):
            print("Not a recognizable user file.", file=sys.stderr)

