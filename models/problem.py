import json
import sys

class Problem:
    def __init__(self, problem_code, problem_name="", point_value=0, time_limit=0, memory_limit=0, is_public=0):
        self.problem_name = problem_name
        self.problem_code = problem_code
        self.time = time_limit
        self.memory = memory_limit
        self.point_value = point_value
        self.is_public = is_public

    def __eq__ (self, other):
        return self.problem_code == other.problem_code
    
    def __str__(self):
        return self.problem_code
    
    def __repr__(self):
        return "\"{}\"".format(self.problem_code)

    @property
    def file(self):
        return "problems/{0}/{0}.pdf".format(self.problem_code)

    def save(self):
        with open("problems/{0}/{0}.json".format(self.problem_code), "w") as s:
            s.write(str(self.__dict__).replace("'","\""))

    @staticmethod
    def read(problem_code):
        try:
            with open("problems/{0}/{0}.json".format(problem_code),"r") as f:
                d = json.loads(f.read())
            return Problem(d["problem_code"],d["problem_name"],d["point_value"],d["time"],d["memory"],d["is_public"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable problem file, {}.".format(problem_code), file=sys.stderr)
