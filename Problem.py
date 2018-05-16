import json
class Problem:
    def __init__(self, problem_code, problem_name, point_value):
        self.file = "problems/" + problem_code + ".pdf"
        self.problem_name = problem_name
        self.problem_code = problem_code
        self.point_value = point_value
    
#    def save(self):
#        s = open("problems/" + self.problem_code + ".json", "w")
#        s.write(str(self.__dict__).replace("'","\""))
#        s.close()

    def __str__(self):
        return self.problem_code
    def __repr(self):
        return self.problem_code

    @staticmethod
    def read(problem_code):
        try:
            f = open("problems/" + problem_code + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Problem(d["problem_code"],d["problem_name"],d["point_value"])
        except FileNotFoundError:
            print("File Not Found")
