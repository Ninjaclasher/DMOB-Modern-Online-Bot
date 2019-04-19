import database
import datetime
from util import *


class Submission:
    def __init__(self, submission_id, points=0.0, total=0.0, time=0.0, memory=0.0, result="IE", user="",
                 problem="", submission_time=datetime.datetime(1970, 1, 1), source="", deleted=0, contest=None):
        self.submission_id = submission_id
        self.points = points
        self.total = total
        self.time = time
        self.memory = memory
        self.result = result
        self._user = user
        self._problem = problem
        self.submission_time = submission_time
        self.source = source
        self.deleted = deleted
        self.contest = contest

    def db_save(self):
        return (self.submission_id, self.points, self.total, self.time, self.memory, self.result,
                self._user, self._problem, self.submission_time, self.source, self.deleted,
                self.contest.id if self.contest is not None else None)

    def __str__(self):
        return "(Submission {0}: {1} {2}/{3} - {4}s, {5}) by {6} to {7} on {8}"\
                    .format(self.submission_id, self.result, self.points, self.total, round(self.time, 3),
                            to_memory(self.memory), self.user.discord_user, self._problem,
                            to_datetime(self.submission_time))

    def __eq__(self, other):
        return self.submission_id == other.submission_id

    def __lt__(self, other):
        return self.submission_id < other.submission_id

    def is_by(self, user):
        return self.user == user

    @property
    def problem(self):
        return database.problem_list[self._problem]

    @property
    def user(self):
        return database.users[self._user]

    @property
    def verdict_colour(self):
        return VERDICT_COLOUR[self.result]

    @property
    def verdict_full(self):
        return VERDICT_FULL[self.result]

    @property
    def score(self):
        return int(self.points/float(self.total)*100) if self.total > 0 else 0


class SubmissionTestCase:
    def __init__(self, id, submission_id, points=0.0, total=0.0, time=0.0, memory=0, status="IE", case=0, batch=0):
        self.id = id
        self.submission_id = submission_id
        self.case = case
        self.status = status
        self.time = time
        self.memory = memory
        self.points = points
        self.total = total
        self.batch = batch
        self.feedback = ""
        self.output = ""

    def db_save(self):
        return self.id, self.submission_id, self.points, self.total, self.time, self.memory, self.status, self.case, self.batch

    def __eq__(self, other):
        return self.submission_id == other.submission_id


class Judge:
    def __init__(self, id, name, key, deleted=0):
        self.id = id
        self.name = name
        self.key = key
        self.deleted = deleted

    def db_save(self):
        return self.id, self.name, self.key, self.deleted

    def __eq__(self, other):
        return self.name == other.name and self.key == other.key

    def __str__(self):
        return "{0} {1}".format(self.name, self.key)
