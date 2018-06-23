from .user import Player
import json
import sys

class Submission:
    def __init__(self, submission_id, points, total, time, memory, result, user):
        self.submission_id = submission_id
        self.points = points
        self.total = total
        self.time = time
        self.memory = memory
        self.result = result
        self.user = user

    def __str__(self):
        return "(Submission " + str(self.submission_id) + ": " + str(self.result) + " " + str(self.points) + "/" + str(self.total) + " - " + str(round(self.time, 3)) + "s, " + str(self.memory) + "KB) by " + self.user.discord_id

    def __eq__(self, other):
        return self.submission_id == other.submission_id

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
            return Submission(d["submission_id"],d["points"],d["total"],d["time"],d["memory"], d["result"], Player.read(str(d["user"])))
        except (FileNotFoundError, KeyError):
            print("Not a recognizable submission file.", file=sys.stderr)


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
