# fake twenty people, with about twenty data rows
# cluster to two group
# 	#1 like web develop
# 	#2 like financial
# after get k neighbors, you got (k*n) notes
# how r u going to mine the notes?
# 	1. find most read notes
#	2. association rules mining, based on what he read
from faker import Factory
import random,psycopg2,bcrypt

class Person(object):
	"""a person with preference"""
	def __init__(self, name, account, password):
		self.name = name
		self.account= account
		# encode pw
		hashed = bcrypt.hashpw(password, bcrypt.gensalt(10))
		self.password= hashed
		self.items= []

	def like(self, item):
		self.items.append(item)

	def __repr__(self):
		return repr(self.items[:2])

def newUser(person):
	cur.execute(
		'INSERT INTO "Users" (account, name, password, active, "createdAt", "updatedAt") VALUES (%s, %s, %s, %s, NOW(), NOW()) RETURNING id;'
		, (person.account, person.name, person.password, False)
		)
	#conn.commit()
	return cur.fetchone()[0]

def newNote(userId, uri):
	ranges= '[{"start":"/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/p[2]","startOffset":0,"end":"/div[2]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/p[2]","endOffset":148}]'
	cur.execute(
		'INSERT INTO "Notes" (uri, ranges, "UserId", "createdAt", "updatedAt") VALUES (%s, %s, %s, NOW(), NOW());'
		, (uri, ranges, userId)
		)
	#conn.commit()

		
conn = psycopg2.connect("dbname=lidar user=william password=1234")
cur = conn.cursor()
faker = Factory.create()
users= []

# read finance and web
financeFile = open('data/business-list.txt','r')
webFile = open('data/web.txt','r')

# init list of web and financial
fin= [ item.strip('\n') for item in financeFile]
web= [ item.strip('\n') for item in webFile]

# generate ten web men
for x in xrange(10):
	person= Person(faker.name(), faker.free_email(), '1234')
	# like 20-30 random websites in web topic
	i= random.randint(20,30)
	for item in random.sample(web,i):
		person.like(item)
	users.append(person)

# generate ten financial men
for x in xrange(10):
	person= Person(faker.name(), faker.free_email(), '1234')
	# like 20-30 random websites in web topic
	i= random.randint(20,30)
	for item in random.sample(fin,i):
		person.like(item)
	users.append(person)

# insert to db
uidList= []
for user in users:
	uid= newUser(user)
	uidList.append(uid)
	for item in user.items:
		newNote(uid,item)

conn.commit()

#write to file
f = open('list.txt','w')
for uid in uidList:
	string= '{0}\n'.format(uid)
	f.write(string)
f.close()

