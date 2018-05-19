import json

from Problem import *

class Contest:
    def __init__(self, name, problems):
        self.name = name
        self.problems = problems

#    def save(self):
#        s = open("contests/" + self.name + ".json", "w")
#        s.write(str(self.__dict__).replace("'","\""))
#        s.close()

    def __str__(self):
        return ""

    @staticmethod
    def read(name):
        try:
            f = open("contests/" + name + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Contest(d["name"], [Problem.read(x) for x in d["problems"]])
        except FileNotFoundError:
            print("File Not Found")

