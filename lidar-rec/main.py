# read id list
# get all users on list
# find k nearest neighbors
# print distance
import psycopg2,pprint
from collections import Counter
from operator import itemgetter
from fp_growth import find_frequent_itemsets
conn = psycopg2.connect("dbname=lidar user=william password=1234")
cur = conn.cursor()

def distance(userA, userB):
	return len(set(userA.items).intersection( set(userB.items) ))

# if listB is subset of listA
def issubset(listA, listB):
	setA = frozenset([frozenset(element) for element in listA])
	setB = frozenset([frozenset(element) for element in listB])
	return (setB <= setA)

def intersection(listA, listB):
	return (set(listA) & set(listB))

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

	def genPopular(self):
		self.popItems= Counter()
		for neighbor in self.neighbors[:3]:
			for item in Person.users[Person.users.index(neighbor[0])].items:
				if item not in self.items:
					self.popItems[item] += 1

	def fp_growth(self):
		self.assocItems= []
		minsup= 5
		# transactions= top 9 users
		transactions= [Person.users[Person.users.index(user[0])].items for user in self.neighbors[:10] if not user[0]==self.id]
		for itemset in find_frequent_itemsets(transactions, minsup):
			# if length more than 2, and not subset if the user items, 
			# also has at least one instersection
			interc= intersection(self.items, itemset)
			if len(itemset)>=2 and not issubset(self.items, itemset) and interc:
				# format -> (what you have, what you should read)
				recItems= set(itemset)-interc
				pairs= {"own": interc, "rec": recItems}
				self.assocItems.append(pairs)


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
	
## results are intersect with association results
# get n neighbors, n=3
# calculate most read links
#for user in Person.users:
#	user.genPopular()

#for user in Person.users:
#	print user.popItems.most_common(5)

## fp-growth
# calculate asscoiation rules
for user in Person.users:
	user.fp_growth()

# print all
pprint.pprint(Person.users[0].assocItems)
