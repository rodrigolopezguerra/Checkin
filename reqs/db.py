#Imports
import MySQLdb
import datetime
import config
import ui

user = config.user
passwd = config.password
db = config.db
server = config.server

#Initiate curser
db = MySQLdb.connect(user=user, passwd=passwd, host=server, db=db)
c = db.cursor()

class User(object):
	"""A simple User class"""
	def __init__(self, userid, name=None, first_name=None, last_name=None,checkins=None,checkouts=None):
		self.id = userid
		self.name = name
		self.first_name = first_name
		self.last_name = last_name
		self.checkins = checkins
		self.checkouts = checkouts

class Checkin(object):
	"""A simple Checkin class"""
	def __init__(self, id, year=None, month=None, day=None,time=None):
		self.id = id
		self.year = year
		self.month = month
		self.day = day
		self.time = time

class Checkout(object):
	"""A simple Checkout class"""
	def __init__(self, id, year=None, month=None, day=None,time=None):
		self.id = id
		self.year = year
		self.month = month
		self.day = day
		self.time = time

class deprecated(Exception):
	"""Error for functions that have been deprecated."""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def get_users():
	"""Simple object that returns a list full of all our users info in tuples"""
	z = []
	c.execute("""SELECT * FROM users""")
	x = c.fetchall()
	for id, name, first_name, last_name, checkins, checkouts in x:
		z.append((id, name, first_name, last_name, checkins, checkouts))
	return z

def user_exist(name):
	c.execute("""SELECT * FROM users WHERE name="%s" """ % (name))
	if c.fetchall() == ():
		return False
	else:
		return True


def new_user(fname,lname,checkinz):
	"""Adds a user in format new_user("FirstName", "LastName", True) where true is bool of whether to mark present for today"""
	name = fname+" "+lname
	if user_exist(name) is False:
		c.executemany("""INSERT INTO users ( name, first_name, last_name, checkins, checkouts) VALUES (%s, %s, %s, %s, %s)""", [(name, fname, lname, "0","0")])
		x = osearch("name", name)
		uid = x.id
		if checkinz == True:
			checkin(uid)
		return True
	else:
		ui.usr_err_1()
		return False

def update_user(change_field,change,iden_field,iden):
	"""Update a row in format IDENITY|SELECT FIELD|CHANGE|CHANGE FIELD @bad Replacement of this function is in the works"""
	c.execute("""UPDATE users SET %s = "%s" WHERE %s = "%s" """, (change_field,change,iden_field,iden))
	db.commit()

def county(uid):
	"""Err what?"""
	c.execute("""SELECT * FROM users where id = "%s" """ % (uid))
	for id, name, first_name, last_name, checkins, checkouts in c.fetchall():
		u = User(id, name, first_name, last_name, checkins, checkouts)
		return u

def checkin(tid):
	"""Checks a user in. @planned add more options for selecting user to checkin."""
	now = datetime.datetime.now()
	tyear = now.year
	tmonth = now.month
	tday = now.day
	ttime = str(now.hour)+":"+str(now.minute)+":"+str(now.second)
	c.executemany("""INSERT INTO checkins ( id, year, month, day, time) VALUES (%s, %s, %s, %s, %s)""", [(tid, tyear, tmonth, tday, ttime)])
	db.commit()
	x = county(tid)
	y = int(x.checkins)+1
	c.execute("""UPDATE users SET checkins = %s WHERE id = "%s" """ % (y,tid))

def checkout(tid):
	"""Checks a user out. @planned add more options for selecting user to checkin."""
	now = datetime.datetime.now()
	tyear = now.year
	tmonth = now.month
	tday = now.day
	ttime = str(now.hour)+":"+str(now.minute)+":"+str(now.second)
	c.executemany("""INSERT INTO checkouts ( id, year, month, day, time) VALUES (%s, %s, %s, %s, %s)""", [(tid, tyear, tmonth, tday, ttime)])
	db.commit()
	x = county(tid)
	y = int(x.checkouts)+1
	c.execute("""UPDATE users SET checkouts = %s WHERE id = "%s" """ % (y,tid))

def search(field,value):
	"""Finds a user and return a tuple'd list."""
	f = []
	c.execute("""SELECT * FROM users WHERE %s = "%s" """ % (field,value))
	for id, name, first_name, last_name, checkins, checkouts in c.fetchall():
		f.append((id,name,first_name,last_name,checkins,checkouts))
	return f

def osearch(field,value):
	"""Find a user and return a User object"""
	c.execute("""SELECT * FROM users WHERE %s = "%s" """ % (field,value))
	for id, name, first_name, last_name, checkins, checkouts in c.fetchall():
		f = User(id, name, first_name, last_name, checkins,checkouts)
		return f

def checkins_today(uid):
	"""Checks if any checkins exist for the user today."""
	xy = []
	now = datetime.datetime.now()
	tmonth = now.month
	tday = now.day
	c.execute("""SELECT * FROM checkins WHERE month = %s AND day=%s AND id=%s""" % (tmonth, tday, uid))
	for id, year, month, day, time in c.fetchall():
		xy.append((month,day,time))
		return xy

def checkouts_today(uid):
	"""Checks if any checkins exist for the user today."""
	xy = []
	now = datetime.datetime.now()
	tmonth = now.month
	tday = now.day
	c.execute("""SELECT * FROM checkouts WHERE month = %s AND day=%s AND id=%s""" % (tmonth, tday, uid))
	for id, year, month, day, time in c.fetchall():
		xy.append((month,day,time))
		return xy
		
def checkins(uid):
	"""Get all checkins for a user @planned add more options for selecting users"""
	xy = []
	c.execute("""SELECT * FROM checkins WHERE id = "%s" """ % (uid))
	for id, year, month, day, time in c.fetchall():
		xy.append((year,month,day,time))
	return xy

def checkouts(uid):
	"""Get all checkouts for a user @planned add more options for selecting users"""
	xy = []
	c.execute("""SELECT * FROM checkouts WHERE id = "%s" """ % (uid))
	for id, year, month, day, time in c.fetchall():
		xy.append((year,month,day,time))
	return xy

def cquery(field,value):
	"""Gets checkins for a user depending on options you give it. Returns tuple of number of checkins and another tuple of ("id", "time") """
	xy = [0]
	xz = []
	c.execute("""SELECT a.id as id,c.name as name,a.time as atime,b.time as btime FROM checkins a  JOIN checkouts b JOIN users c on a.id=c.id and a.id=b.id and a.%s = b.%s WHERE a.%s = "%s" """ % (field,field,field,value))
	for id, name, atime, btime in c.fetchall():
		xy[0] += 1
		xz.append((id,name,atime,btime))
	return (xy,xz)

def out_cquery(field,value):
	"""Gets checkout for a user depending on options you give it. Returns tuple of number of checkins and another tuple of ("id", "time") """
	xy = [1]
	xz = []
	c.execute("""SELECT * FROM checkouts WHERE %s = "%s" """ % (field,value))
	for id, year, month, day, time in c.fetchall():
		xy[0] += 1
		xz.append((id,time))
	return (xy,xz)

########################
##DEPRECATED FUNCTIONS##
########################
def find_user(field,value):
	"""@DEPRECATED use search()"""
	try:
		raise deprecated("search()")
	except deprecated as e:
		print 'This function or class has been deprecated in place of: ', e.value

def add_user(fname,lname,checkins):
	"""@DEPRECATED use new_user()"""
	try:
		raise deprecated("new_user()")
	except deprecated as e:
		print 'This function or class has been deprecated in place of: ', e.value

def dfind_user(field1,field2,value1,value2):
	"""@DEPRECATED use search()"""
	try:
		raise deprecated("search()")
	except deprecated as e:
		print 'This function or class has been deprecated in place of: ', e.value

