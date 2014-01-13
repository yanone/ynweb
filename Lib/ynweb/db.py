class MySQL:
	def __init__(self, user, password, name, host):
		self.user = user
		self.password = password
		self.name = name
		self.host = host
		self.connected = False

	def connect(self):
		if not self.connected:
			
			import MySQLdb
			from DBUtils.PooledDB import PooledDB

			self.pool = PooledDB(creator = MySQLdb, mincached = 5, db = self.name, host = self.host, user = self.user, passwd= self.password, charset = "utf8", use_unicode = True)
			self.conn = self.pool.connection(0)
			self.cursor = self.conn.cursor ()
			self.connected = True

	def unclutter(self, x):
		return x[0]

	def put(self, db, ID, key, value):
		self.connect()
		# update
		if ID:
			self.cursor.execute("UPDATE %s SET %s = '%s' WHERE ID = '%s' ;" % (db, key, value, ID))
		# create new
		else:
			self.cursor.execute("INSERT INTO %s (%s) VALUES ('%s') ;" % (db, key, value))
			self.cursor.execute("SELECT max(ID) from %s" % (db))
			return self.cursor.fetchone()[0]
		self.conn.commit()
	
	#"INSERT INTO fontnames idth', 'style_name') VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (db['fontnames'][i]['family'], db['fontnames'][i]['family_name'], db['fontnames'][i]['bold'], db['fontnames'][i]['italic'], db['fontnames'][i]['weight'], db['fontnames'][i]['weight_code'], db['fontnames'][i]['width'], db['fontnames'][i]['style_name']))

	def get(self, db, ID, key):
		self.connect()
		string = "SELECT %s FROM %s WHERE ID = '%s' ;" % (key, db, ID)
	#	print string
		self.cursor.execute(string)
		return self.cursor.fetchone()[0]
	
	def fetchone(self, statement):
		self.connect()
		self.cursor.execute(statement)
		answer = self.cursor.fetchone()
	
		return answer

	def dbexec(self, statement):
		self.connect()
		self.cursor.execute(statement)
		self.conn.commit()
		answer = self.cursor.fetchall()
	
	#	Main.debug(statement)
	#	Main.debug(answer)
	
		return answer
	
	def commit(self):
		self.connect()
		self.conn.commit()
	#	cursor.close()
	#	connection.close()