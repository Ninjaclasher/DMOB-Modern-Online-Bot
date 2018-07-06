import database

from .submission import Submission

class Contest:
    def __init__(self, id, name, problems, deleted=0):
        self.id = id
        self.name = name
        self._problems = problems
        self.deleted = deleted
    
    def db_save(self):
        return self.id, self.name, self.deleted

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name
    
    @property
    def problems(self):
        return [database.problem_list[x] for x in self._problems]

class ContestPlayer:
    def __init__(self,user,contest=None):
        self.user = user
        self.contest = contest
        self._best_submissions = None
        if contest is not None:
            self.update_best()

    def __eq__(self,other):
        return self.user == other.user

    def update_best(self):
        self._best_submissions = database.get_best_contest_submissions(self.user, self.contest)

    @property
    def best_submissions(self):
        return [x[0] for x in self._best_submissions]

    @property
    def total_score(self):
        values = list(map(sum,zip(*self._best_submissions)))
        values[1] = -values[1]
        return values
