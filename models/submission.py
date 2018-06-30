import database
import json
import os
import sys
import time
from .user import Player
from .problem import Problem
from util import *

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
        return "(Submission {0}: {1} {2}/{3} - {4}s, {5}) by {6} to {7} on {8}".format(self.submission_id, self.result, self.points, self.total, round(self.time, 3), to_memory(self.memory), self.user.discord_user, self.problem, to_datetime(self.submission_time))
    
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
        return open("submissions/{0}/{0}.code".format(self.submission_id), "r").read()

    def save(self):
        Submission.prepare_save(self.submission_id)
        with open("submissions/{0}/{0}.json".format(self.submission_id), "w") as s:
            s.write(str(self.__dict__).replace("'","\""))
    
    @staticmethod
    def prepare_save(id):
        if not os.path.isdir("submissions/{}".format(id)):
            os.mkdir("submissions/{}".format(id))
        if not os.path.isdir("submissions/{}/cases".format(id)):
            os.mkdir("submissions/{}/cases".format(id))            

    @staticmethod
    def save_code(id, code):
        Submission.prepare_save(id)
        with open("submissions/{0}/{0}.code".format(id), "w") as s:
            s.write(code)

    @staticmethod
    def read(submission_id):
        try:
            with open("submissions/{0}/{0}.json".format(submission_id), "r") as f:
                d = json.loads(f.read())
            return Submission(d["submission_id"],d["points"],d["total"],d["time"],d["memory"], d["result"], database.users[str(d["user"])], database.problem_list[str(d["problem"])], d["submission_time"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable submission file, {}.".format(submission_id), file=sys.stderr)

class SubmissionTestCase:
    def __init__(self, submission_id, case, status="", time=0.0, memory=0.0, points=0.0, total=0.0, batch=0):
        self.submission_id = submission_id
        self.case = case
        self.status = status
        self.time = time
        self.memory = memory
        self.points = points
        self.total = total
        self.batch = batch

    def __eq__(self, other):
        return self.submission_id == other.submission_id
    
    def __hash__(self):
        return self.case

    def save(self):
        with open("submissions/{0}/cases/{1}.json".format(self.submission_id, self.case), "w") as s:
            s.write(str(self.__dict__).replace("'", "\""))

    @staticmethod
    def read(submission_id, submission_case):
        try:
            with open("submissions/{0}/cases/{1}.json".format(submission_id, submission_case), "r") as f:
                d = json.loads(f.read())
            return SubmissionTestCase(d["submission_id"], d["case"], d["status"], d["time"], d["memory"], d["points"], d["total"], d["batch"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable submission case file, {}-{}".format(submission_id, submission_case), file=sys.stderr)

class Judge:
    def __init__(self, id, key):
        self.id = id
        self.key = key

    def __eq__(self, other):
        return self.id == other.id and self.key == other.key

    def __str__(self):
        return "{0} {1}".format(self.id, self.key)
