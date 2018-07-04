import database
from bisect import bisect
from collections import defaultdict
from util import *

class Player:
    def __init__(self,id,points=0,language=DEFAULT_LANG,is_admin=0):
        self.id = id
        self.points = points
        self.language = language
        self.is_admin = is_admin

    def __eq__(self, other):
        return self.id == other.id
    
    def db_save(self):
        return self.id, self.points, self.language, self.is_admin

    async def update_points(self):
        with await database.locks["user"][self.id]:
            max_subs = defaultdict(lambda: 0.0)
            for x in self.submissions:
                max_subs[x.problem.code] = max(max_subs[x.problem.code], x.points/x.total*x.problem.point_value if x.total > 0 else 0)
            self.points = sum(max_subs.values())

    @property
    def discord_user(self):
        return database.discord_users_list[str(self.id)]

    @property
    def rank(self):
        return database.get_ranks(self)

    @property
    def rating(self):
        return 1200 if not self.rated else self.rank[-1].rating

    @property
    def volatility(self):
        return 385 if not self.rated else self.rank[-1].volatility

    @property
    def rank_title(self):
        if not self.rated:
            return RANKING_TITLES[0]
        return RANKING_TITLES[bisect(RANKING_VALUES, self.rating)-1]
    
    @property
    def rank_colour(self):
        if not self.rated:
            return RANKING_COLOUR[0]
        return RANKING_COLOUR[bisect(RANKING_VALUES, self.rating)-1]
            
    @property
    def rated(self):
        return len(self.rank) > 0

    @property
    def submissions(self):
        return database.get_submissions(self)

class Rank:
    def __init__(self, id, user, rating, volatility):
        self.id = id
        self.user = user
        self.rating = rating
        self.volatility = volatility
    
    def db_save(self):
        return self.id, self.user, self.rating, self.volatility

