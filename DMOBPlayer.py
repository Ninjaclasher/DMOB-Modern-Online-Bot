import json
class DMOBPlayer:
	def __init__(self,name,discord_id,points,rank,language):
		self.name = name
		self.discord_id = discord_id
		self.points = points
		self.rank = rank
		self.language = language

	def save(self):
		s = open("players\\"+self.name + ".json", "w")
		s.write(str(self.__dict__).replace("'","\""))
		s.close()

	def __repr__(self):
		return "DMOBPlayer('{}','{}','{}','{}','{}')".format(self.name,self.discord_id,self.points,self.rank,self.language)

	def __str__(self):
		return "Name: {}, Points: {}, Rank: {}".format(self.name,self.points,self.rank)

	@staticmethod
	def read(name):
		try:
			f = open("players\\"+name+".json","r")
			d = json.loads(f.read())
			f.close()
			return DMOBPlayer(d["name"],d["discord_id"],d["points"],d["rank"],d["language"])
		except FileNotFoundError:
			print("File Not Found")
		
