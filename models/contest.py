import json
import sys

from .problem import Problem
from .submission import Submission
import database

class Contest:
    def __init__(self, name, problems):
        self.name = name
        self.problems = problems

    def save(self):
        with open("contests/" + self.name + ".json", "w") as s:
            s.write(str(self.__dict__).replace("'","\""))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def read(name):
        try:
            with open("contests/" + name + ".json","r") as f:
                d = json.loads(f.read())
            return Contest(d["name"], [database.problem_list[x] for x in d["problems"]])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable contest file, " + str(name) + ".", file=sys.stderr)

class ContestPlayer:
    def __init__(self,user,num_problems):
        self.user=user
        self.submissions=[[] for x in range(num_problems)]
    
    def __eq__(self,other):
        return self.user == other.user

    @property
    def best_submissions(self):
        return [max(x, default=ContestSubmission(None, -1, 0.0, 0.0, 0, 0, "UK", None, None, 0), key=lambda y: [y.score, -y.submission_time]) for x in self.submissions]

    @property
    def total_score(self):
        return [sum(x.score for x in self.best_submissions), -sum(x.submission_time for x in self.best_submissions)]

class ContestSubmission(Submission):
    def __init__(self, game, *args):
        self.contest = game
        super(ContestSubmission, self).__init__(*args)

    @property
    def score(self):
        return int(self.points/float(self.total)*100) if self.total > 0 else 0

