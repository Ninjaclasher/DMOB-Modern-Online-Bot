import os

import Contest
import DMOBPlayer
import Problem
help_list = {
    "help": "",
    "contest":"",
    "language":"",

}
languages = ["cpp", "java8", "turing", "python2", "python3", "pypy2", "pypy3"]
two_commands = ["contest", "language"]
contest_list = [Contest.read(x.split(".")[0]) for x in os.listdir("contests") if x.split(".")[1] == "json"]
problem_list = [Problem.read(x.split(".")[0]) for x in os.listdir("problems") if x.split(".")[1] == "json"]
users = {}
for x in os.listdir("players"):
    x = x.split(".")
    if x[1] == "json":
        users[x[0]] = DMOBPlayer.read(x[0])
