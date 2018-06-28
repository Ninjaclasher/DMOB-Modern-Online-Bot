from .user import Player
from .problem import Problem
from util import *
import database
import json
import sys
import time

class Submission:
    def __init__(self, submission_id, points=0.0, total=0.0, time=0.0, memory=0.0, result="IE", user=None, problem=None, submission_time=time.time()):
        self.submission_id = submission_id
        self.points = points
        self.total = total
        self.time = time
        self.memory = memory
        self.result = result
        self.user = user
        self.problem = problem
        self.submission_time=submission_time

    def __str__(self):
        return "(Submission {0}: {1} {2}/{3} - {4}s, {5}) by {6} to {7} at {8}".format(self.submission_id, self.result, self.points, self.total, round(self.time, 3), to_memory(self.memory), self.user.discord_user, self.problem, to_datetime(self.submission_time))
    
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
        return open("submissions/{}.code".format(self.submission_id), "r").read()

    def save(self):
        with open("submissions/" + str(self.submission_id) + ".json", "w") as s:
            s.write(str(self.__dict__).replace("'","\""))

    @staticmethod
    def read(submission_id):
        try:
            with open("submissions/{}.json".format(submission_id), "r") as f:
                d = json.loads(f.read())
            return Submission(d["submission_id"],d["points"],d["total"],d["time"],d["memory"], d["result"], database.users[str(d["user"])], database.problem_list[str(d["problem"])], d["submission_time"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable submission file, {}.".format(submission_id), file=sys.stderr)

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
        return "{0} {1}".format(self.id, self.key)
