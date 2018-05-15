class Contest:
    def __init__(self, name, problems):
        self.name = name
        self.problems = problems

    def save(self):
        s = open("contests/" + self.name + ".json", "w")
        s.write(str(self.__dict__).replace("'","\""))
        s.close()

    @staticmethod
    def read(name):
        try:
            f = open("contests/" + problem_code + ".json","r")
            d = json.loads(f.read())
            f.close()
            return Problem(d["name"],d["name"],d["point_value"])
        except FileNotFoundError:
            print("File Not Found")

