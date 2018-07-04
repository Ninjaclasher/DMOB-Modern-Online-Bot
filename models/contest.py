import database

from .submission import Submission

class Contest:
    def __init__(self, id, name, problems):
        self.id = id
        self.name = name
        self._problems = problems
    
    def db_save(self):
        return self.id, self.name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name
    
    @property
    def problems(self):
        return [database.problem_list[x] for x in self._problems]

class ContestPlayer:
    def __init__(self,user,problems=[]):
        self.user=user
        self.submissions={}
        for x in problems:
            self.submissions[x.code] = []

    def __eq__(self,other):
        return self.user == other.user

    @property
    def best_submissions(self):
        return [max(x, default=Submission(-1), key=lambda y: [y.score, -y.submission_time]) for x in self.submissions.values()]

    @property
    def total_score(self):
        return [sum(x.score for x in self.best_submissions), -sum(x.submission_time for x in self.best_submissions)]

