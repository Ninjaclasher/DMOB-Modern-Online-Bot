import database

class Problem:
    def __init__(self, id=None, name="", code="", author="", time_limit=0, memory_limit=0, point_value=0, is_public=0):
        self.id = id
        self.name = name
        self.code = code
        self._user = author
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.point_value = point_value
        self.is_public = is_public
    
    def __eq__ (self, other):
        return self.code == other.code
    
    def db_save(self):
        return self.id, self.name, self.code, self._user, self.time_limit, self.memory_limit, self.point_value, self.is_public
    
    @property
    def file(self):
        return "problems/{0}.pdf".format(self.id)
    
    @property
    def author(self):
        return database.users[self._user]
