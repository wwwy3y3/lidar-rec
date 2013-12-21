# read id list
# get all users on list
# find k nearest neighbors
# print distance
import psycopg2,copy
from operator import itemgetter
conn = psycopg2.connect("dbname=lidar user=william password=1234")
cur = conn.cursor()

def distance(userA, userB):
	return len(set(userA.items).intersection( set(userB.items) ))

class Person(object):
	"""a person with preference"""
	users= [] # all users

	def __init__(self, id):
		self.id= id
		self.items= []
		self.neighbors= []

	def like(self, item):
		self.items.append(item)

	def fetch(self):
		cur.execute(
			'SELECT * FROM "Notes" WHERE "UserId"=%s;'
			, (self.id,)
			)
		for item in cur.fetchall():
			self.like(item[3])

	def findNeighbors(self):
		for user in Person.users:
			if not self==user:
				self.neighbors.append((user.id,distance(self,user)))
		self.neighbors= sorted(self.neighbors, key= itemgetter(1), reverse= True)

	def __eq__(self, id):
		return self.id == id

# init
uidList = open('data/list.txt','r')
for uid in uidList:
	person= Person(int(uid))
	person.fetch()
	Person.users.append(person)

# find neighbor
for user in Person.users:
	user.findNeighbors()

# get n neighbors
#for user in Person.users:
for item in Person.users[0].neighbors[:5]:
	user= Person.users[Person.users.index(item[0])]
	print user.items[:1]