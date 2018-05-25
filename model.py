import json
__all__ = ['Submission', 'SubmissionTestCase', 'Problem', 'Contest', 'Player', 'ContestPlayer']


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


class Problem:
    def __init__(self, problem_code, problem_name, point_value, time_limit, memory_limit):
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
        except (FileNotFoundError, KeyError):
            import sys
            print("Not a recognizable problem file.", file=sys.stderr)

class Contest:
    def __init__(self, name, problems):
        self.name = name
        self.problems = problems

    def save(self):
        s = open("contests/" + self.name + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __str__(self):
        return ""

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def read(name):
        try:
            f = open("contests/" + name + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Contest(d["name"], [Problem.read(x) for x in d["problems"]])
        except (FileNotFoundError, KeyError):
            import sys
            print("Not a recognizable contest file.", file=sys.stderr)

class Player:
    def __init__(self,discord_id,points,rank,language,is_admin):
        self.discord_id = discord_id
        self.points = points
        self.rank = rank
        self.language = language
        self.is_admin = is_admin

    def save(self):
        s = open("players/" + str(self.discord_id) + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    def __repr__(self):
        return "Player('{}','{}','{}','{}','{}')".format(self.discord_id,self.points,self.rank,self.language,self.is_admin)

    def __str__(self):
        return "ID: {}, Points: {}, Rank: {}".format(self.discord_id,self.points,self.rank)

    def __eq__(self, other):
        return self.discord_id == other.discord_id

    @staticmethod
    def read(discord_id):
        try:
            f = open("players/" + discord_id + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Player(d["discord_id"],d["points"],d["rank"],d["language"],d["is_admin"])
        except (FileNotFoundError, KeyError):
            import sys
            print("Not a recognizable user file.", file=sys.stderr)

class ContestPlayer:
    def __init__(self,user,discord_user,num_problems):
        self.user=user
        self.discord_user=discord_user
        self.problems=[0]*num_problems
        self.time=[0]*num_problems

    def __eq__(self,other):
        return self.user == other.user

