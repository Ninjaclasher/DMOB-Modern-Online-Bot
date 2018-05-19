class ContestPlayer:
    def __init__(self,user,num_problems):
        self.user=user
        self.problems=[0]*num_problems

    def __eq__(self,other):
        return self.user == other.user
