import json

from discord import *

class DMOBPlayer:
    def __init__(self,discord_id,points,rank,language):
        self.discord_id = discord_id
        self.points = points
        self.rank = rank
        self.language = language

    def save(self):
        s = open("players/" + str(self.discord_id) + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __repr__(self):
        return "DMOBPlayer('{}','{}','{}','{}')".format(self.discord_id,self.points,self.rank,self.language)

    def __str__(self):
        return "ID: {}, Points: {}, Rank: {}".format(self.discord_id,self.points,self.rank)

    @staticmethod
    def read(discord_id):
        try:
            f = open("players/" + discord_id + ".json","r")
            d = json.loads(f.read())
            f.close()
            return DMOBPlayer(d["discord_id"],d["points"],d["rank"],d["language"])
        except FileNotFoundError:
            print("File Not Found")
