# -*- coding: utf-8 -*-

import cgi, os, re



class YNWeb(object):
	def __init__(self, environ, start_response, db_user = None, db_password = None, db_name = None, db_host = None):
		self.environ = environ
		self.start_response = start_response
		self.session = self.environ['beaker.session']
		self.sessionaltered = False
		
		self.db = None
		self.db_user = db_user
		self.db_password = db_password
		self.db_name = db_name
		self.db_host = db_host
		if self.db_user and self.db_password and self.db_name and self.db_host:
			import db
			reload(db)
			self.db = db.MySQL(self.db_user, self.db_password, self.db_name, self.db_host)
		
		
		# PROCESS FORM INPUT
		self.form = None
		if self.environ['REQUEST_METHOD'] == 'POST':
			self.form = cgi.FieldStorage(fp=self.environ['wsgi.input'], environ=self.environ) 
		elif self.environ['REQUEST_METHOD'] == 'GET':
			self.form = cgi.FieldStorage(fp=self.environ['QUERY_STRING'], environ=self.environ) 

		##################################################
		#
		#		Recognize environment.
		#	
		#		platform: iOS, Macintosh, Linux, Windows
		#		browser: Firefox, Safari, MobileSafari, InternetExplorer, Opera, Chrome
		#		browserversion: 0.0 as float value
		#		device: iPad, iPhone
		#		devicecatgegory: Desktop, Mobile
		#
		#		supportsSVG: True/False
		#
		##################################################

		self.platform = None
		self.browser = None
		self.browserversion = None
		self.device = None
		self.devicecategory = None
		self.supportsSVG = False

		if self.environ.has_key('HTTP_USER_AGENT'):

		
			# OS / device category
			if 'like Mac OS X' in self.environ['HTTP_USER_AGENT']:
				self.platform = 'iOS'
				self.devicecategory = 'Mobile'
			elif 'Macintosh' in self.environ['HTTP_USER_AGENT']:
				self.platform = 'Macintosh'
				self.devicecategory = 'Desktop'
			elif 'Linux' in self.environ['HTTP_USER_AGENT']:
				self.platform = 'Linux'
				self.devicecategory = 'Desktop'
			elif 'Windows' in self.environ['HTTP_USER_AGENT']:
				self.platform = 'Windows'
				self.devicecategory = 'Desktop'

			# device
			if 'iPad' in self.environ['HTTP_USER_AGENT']:
				self.device = 'iPad'
			elif 'iPhone' in self.environ['HTTP_USER_AGENT']:
				self.device = 'iPhone'


			### BROWSER

			try:
				# Firefox
				if 'Firefox' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'Firefox'
					m = re.search(r"Firefox/(\d+\.\d+)", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))

				# Chrome
				if 'Chrome' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'Chrome'
					m = re.search(r"Chrome/(\d+\.\d+)", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))

				# Safari
				elif 'Safari' in self.environ['HTTP_USER_AGENT'] and not 'Mobile' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'Safari'
					m = re.search(r"/(\d+\.\d+).*?Safari", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))

				# Mobile Safari
				elif 'Safari' in self.environ['HTTP_USER_AGENT'] and 'Mobile' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'MobileSafari'
					m = re.search(r"/(\d+\.\d+).*?Mobile.*?Safari", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))

				# Opera
				elif 'Opera' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'Opera'
					m = re.search(r"Version/(\d+\.\d+)", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))

				# IE
				elif 'MSIE' in self.environ['HTTP_USER_AGENT']:
					self.browser = 'InternetExplorer'
					m = re.search(r"MSIE (\d+\.\d+)", self.environ['HTTP_USER_AGENT'])
					self.browserversion = float(m.group(1))
			except:
				pass

			# SVG support
		
			# http://de.wikipedia.org/wiki/Scalable_Vector_Graphics
			if self.browser == 'Opera' and self.browserversion >= 9.0:
				self.supportsSVG = True
			elif (self.browser == 'Safari' or self.browser == 'MobileSafari') and self.browserversion >= 3.2:
				self.supportsSVG = True
			elif self.browser == 'Chrome' and self.browserversion >= 4.0:
				self.supportsSVG = True
			elif self.browser == 'Firefox' and self.browserversion >= 3.0:
				self.supportsSVG = True
			elif self.browser == 'InternetExplorer' and self.browserversion >= 9.0:
				self.supportsSVG = True


		########### END ENVIRONMENT ########### 
			
	def encode(self, string):
#		if isinstance(string, str):
#			return unicode(string)
#		elif isinstance(string, unicode):
#			return string
#		else:
#			return unicode(str(string))
		string = string.encode('utf-8')
		return string
	
	def smartString(self, s, encoding='utf-8', errors='strict', from_encoding='utf-8'):
		import types
		if type(s) in (int, long, float, types.NoneType):
			return str(s)
		elif type(s) is str:
			if encoding != from_encoding:
				return s.decode(from_encoding, errors).encode(encoding, errors)
			else:
				return s
		elif type(s) is unicode:
			return s.encode(encoding, errors)
		elif hasattr(s, '__str__'):
			return self.smartString(str(s), encoding, errors, from_encoding)
		elif hasattr(s, '__unicode__'):
			return self.smartString(unicode(s), encoding, errors, from_encoding)
		else:
			return self.smartString(str(s), encoding, errors, from_encoding)
		
	# INPUT
	def input(self, key):
		if self.form:
			if self.form.has_key(key):
				return self.smartString(self.form.getfirst(key))

	def file(self, key):
		if self.form.has_key(key):
			return UploadFile(self.form[key].filename, self.form[key].file.read())

	# OUTPUT
	def content(self, responseCode, contentType, content, contentDisposition = None):

		content = self.smartString(content)

		if self.sessionaltered:
			self.session.save()

		responseList = [
			('Content-type', contentType),
			('Content-Length', self.smartString(len(content))),
			]
		if contentDisposition:
			responseList.append(('Content-Disposition', contentDisposition))
		
		
		self.start_response(responseCode, responseList)
		return content


	def response(self, content, contentType = 'text/plain', responseCode = '200', contentDisposition = None):
		return Response(self, content, contentType, responseCode, contentDisposition)

	def saveSession(self):
		if self.sessionaltered:
			self.session.save()

	# SESSION
	def getSession(self, key):
		if self.session.has_key(key):
			return self.session[key]

	def setSession(self, key, value):
		self.session[key] = value
		self.sessionaltered = True


	def processInput(self, fields, requiredfields):
		self.inputOK = True

		# FAULTY CHARACTERS
		self.faulty = []
		def singleHex(string):
			if len(string) == 1:
				return '%' + hex(ord(string))[2:]
			else:
				return ''

		triggers = (
			"'",
			":",
			";",
#			"/",
			"\\",
			"!",
			"\"",
#			"#",
			"?",
#			"=",
	#		"@",
			"%",
			"<",
			">",
			"$",
	#		"&",
			"[",
			"]",
			"~",
			"^",
			"`",
			"{",
			"}",
			"|",
		)
		faulty = []
		for key in fields.keys():
			if self.input(key):
				for trigger in triggers:
					if trigger in self.input(key).lower() or singleHex(trigger) and (singleHex(trigger) in self.input(key).lower()):
						if not key in self.faulty:
							self.faulty.append(key)
							self.inputOK = False

		# REQUIRED
		self.requiredmissing = []
		for key in requiredfields:
			if key != None:
				if not self.input(key) or self.input(key) == '--empty--':
						if not key in self.requiredmissing:
							self.requiredmissing.append(key)
							self.inputOK = False


class Response(object):
	
	responses = {
		'200': 'OK',
		'404': 'Not Found',
	}
	
	def __init__(self, parent, content, contentType = 'text/plain', responseCode = '200', contentDisposition = None):
		self.parent = parent
		self.responseCode = str(responseCode)
		self.content = content
		self.contentType = contentType
		self.contentDisposition = contentDisposition

	def respond(self, start_response):
		self.start_response = start_response
		
		self.parent.saveSession()

		responseList = [
			('Content-type', self.contentType),
			('Content-Length', str(len(self.content))),
			]
			
		if self.responseCode in self.responses:
			response = "%s %s" % (self.responseCode, self.responses[self.responseCode])
		else:
			response = str(self.responseCode)
		
		if self.contentDisposition:
			responseList.append(('Content-Disposition', self.contentDisposition))
		
		# Send response
		self.start_response(response, responseList)
		return self.parent.smartString(self.content)


class UploadFile(object):
	def __init__(self, filename, content):
		self.filename = filename
		self.content = content
		self.ending = self.filename.lower().split('.')[-1]

	def save(self, folder, filename = None):
		if self.content:
			if filename:
				if '.' in filename:
					path = os.path.join(folder, filename)
				else:
					path = os.path.join(folder, filename + '.' + self.ending)
			else:
				path = os.path.join(folder, self.filename)
		
			fout = open(path, 'wb')
			fout.write(self.content)
			fout.close()
		

######### SECURITY

def makeHash(string):
	u'''\
	Create hex hash string with SHA512.
	'''
	import hashlib
	return hashlib.sha512(string).hexdigest()
	