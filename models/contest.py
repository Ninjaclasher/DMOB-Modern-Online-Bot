import json
import sys

from .problem import Problem

class Contest:
    def __init__(self, name, problems):
        self.name = name
        self.problems = problems

    def save(self):
        s = open("contests/" + self.name + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __str__(self):
        return ""

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def read(name):
        try:
            f = open("contests/" + name + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Contest(d["name"], [Problem.read(x) for x in d["problems"]])
        except (FileNotFoundError, KeyError):
            print("Not a recognizable contest file.", file=sys.stderr)

class ContestPlayer:
    def __init__(self,user,discord_user,num_problems):
        self.user=user
        self.discord_user=discord_user
        self.problems=[0]*num_problems
        self.time=[0]*num_problems

    def __eq__(self,other):
        return self.user == other.user
