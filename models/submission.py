class Submission:
    def __init__(self, submission_id, points, total, time, memory, result):
        self.submission_id = submission_id
        self.points = points
        self.total = total
        self.time = time
        self.memory = memory
        self.result = result

    def __str__(self):
        return "(Submission " + str(self.submission_id) + ": " + str(self.result) + " " + str(self.points) + "/" + str(self.total) + " - " + str(round(self.time, 3)) + "s, " + str(self.memory) + "KB)"

    def __eq__(self, other):
        return self.submission_id == other.submission_id

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
