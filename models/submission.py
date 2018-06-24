from .user import Player
from .problem import Problem
import database
import json
import sys

class Submission:
    def __init__(self, submission_id, points=0.0, total=0.0, time=0.0, memory=0.0, result="IE", user=None, problem=None):
        self.submission_id = submission_id
        self.points = points
        self.total = total
        self.time = time
        self.memory = memory
        self.result = result
        self.user = user
        self.problem = problem

    def __str__(self):
        return "(Submission " + str(self.submission_id) + ": " + str(self.result) + " " + str(self.points) + "/" + str(self.total) + " - " + str(round(self.time, 3)) + "s, " + str(self.memory) + "KB) by " + str(self.user.discord_user)  + " to " + str(self.problem)

    def __eq__(self, other):
        return self.submission_id == other.submission_id
    
    def __lt__(self, other):
        return self.submission_id < other.submission_id
    
    def __hash__(self):
        return self.submission_id

    def is_by(self, user):
        return self.user == user

    @property
    def source(self):
        return open("submissions/" + str(self.submission_id) + ".code", "r").read()

    def save(self):
        s = open("submissions/" + str(self.submission_id) + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    @staticmethod
    def read(submission_id):
        try:
            f = open("submissions/" + str(submission_id) + ".json", "r")
            d = json.loads(f.read())
            f.close()
            return Submission(d["submission_id"],d["points"],d["total"],d["time"],d["memory"], d["result"], database.users[str(d["user"])], database.problem_list[str(d["problem"])])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable submission file, " + str(submission_id) + ".", file=sys.stderr)


class SubmissionTestCase:
    def __init__(self, submission_id, case):
        self.submission_id = submission_id
        self.case = case
        self.status = ''
        self.time = 0.0
        self.memory = 0.0
        self.points = 0.0
        self.total = 0.0
        self.batch = 0
        self.feedback = ''
        self.output = ''

        def __eq__(self, other):
            return self.submission_id == other.submission_id

class Judge:
    def __init__(self, id, key):
        self.id = id
        self.key = key

    def __eq__(self, other):
        return self.id == other.id and self.key == other.key

    def __str__(self):
        return str(self.id) + " " + str(self.key)
