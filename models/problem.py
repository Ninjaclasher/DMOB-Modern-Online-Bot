import json
import sys

class Problem:
    def __init__(self, problem_code, problem_name="", point_value=0, time_limit=0.0, memory_limit=0):
        self.file = "problems/" + problem_code + "/" + problem_code + ".pdf"
        self.problem_name = problem_name
        self.problem_code = problem_code
        self.time = time_limit
        self.memory = memory_limit
        self.point_value = point_value
    
    def save(self):
        s = open("problems/" + self.problem_code + "/" + self.problem_code + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __eq__ (self, other):
        return self.problem_code == other.problem_code
    def __str__(self):
        return self.problem_code
    def __repr__(self):
        return "\"" + self.problem_code + "\""

    @staticmethod
    def read(problem_code):
        try:
            f = open("problems/" + problem_code + "/" + problem_code + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Problem(d["problem_code"],d["problem_name"],d["point_value"],d["time"],d["memory"])
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            print("Not a recognizable problem file, " + str(problem_code) + ".", file=sys.stderr)
