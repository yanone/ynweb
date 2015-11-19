# -*- coding: utf-8 -*-

import cgi, os, re


class YNWeb(object):
	def __init__(self, environ, start_response, db_user = None, db_password = None, db_name = None, db_host = None):
		self.environ = environ
		self.start_response = start_response
		try:
			self.session = self.environ['beaker.session']
		except:
			self.session = None
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
		self.inputFields = {}
		self.fileObjects = {}


		# PROCESS FORM INPUT
		if self.environ['REQUEST_METHOD'] == 'POST':
#			post_env = self.environ.copy()
#			post_env['QUERY_STRING'] = ''
#			self.form = cgi.FieldStorage(fp=self.environ['wsgi.input'], environ=post_env, keep_blank_values=True) 
			self.form = cgi.FieldStorage(fp=self.environ['wsgi.input'], environ=self.environ, keep_blank_values=True)
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
			if self.browser == 'Opera' and self.browserversion >= 11.01:
				self.supportsSVG = True
			elif (self.browser == 'Safari' or self.browser == 'MobileSafari') and self.browserversion >= 5.0:
				self.supportsSVG = True
			elif self.browser == 'Chrome' and self.browserversion >= 10.0:
				self.supportsSVG = True
			elif self.browser == 'Firefox' and self.browserversion >= 4.0:
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
		import urllib
		
		if hasattr(self, 'form') and self.form.has_key(key):
			
			if self.inputFields.has_key(key):
				if self.inputFields[key] == bool:
					value = self.form.getfirst(key)
				
					if value == 'True' or value == 'true' or value == '1' or value == 'on':
						return True
					elif value == 'False' or value == 'false' or value == '0' or value == '':
						return False
				
				elif self.inputFields[key] == int:
					return int(self.form.getfirst(key))

				elif self.inputFields[key] == unicode:
					return self.smartString(urllib.unquote(self.form.getfirst(key).decode('utf8')))

				elif self.inputFields[key] == str:
					return self.smartString(urllib.unquote(self.form.getfirst(key)))

				elif self.inputFields[key] == 'file':
					return self.form.getfirst(key)

				else:
					return urllib.unquote(self.form.getfirst(key))
			else:
				return urllib.unquote(self.form.getfirst(key))
		else:
			return ''
			#urllib.unquote(url).decode('utf8')

	def file(self, key):
		if self.form[key].file:
			
			if not self.fileObjects.has_key(key):
				self.fileObjects[key] = UploadFile(self.form[key].filename, self.form[key].file.read())
			
			return self.fileObjects[key]

	def response(self, content, contentType = 'text/plain', responseCode = '200', header = None):
		return Response(self, content, contentType, responseCode, header)

	def redirect(self, url):
		return Response(self, responseCode = '301', header = ('Location', url))

	def saveSession(self):
		if self.session:
			if self.sessionaltered:
				self.session.save()

	# SESSION
	def getSession(self, key):
		if self.session:
			if self.session.has_key(key):
				return self.session[key]

	def setSession(self, key, value):
		if self.session:
			self.session[key] = value
			self.sessionaltered = True


	def processInput(self, fields, requiredfields):
		self.inputOK = True
		self.inputFields = {}

		# FAULTY CHARACTERS
		self.faulty = []
		def singleHex(string):
			if len(string) == 1:
				return '%' + hex(ord(string))[2:]
			else:
				return ''

		faulty = []
		for key in fields.keys():
			
#			if fields[key] == str or fields[key] == unicode:
#				for trigger in triggers:
#					if trigger in self.input(key).lower() or singleHex(trigger) and (singleHex(trigger) in self.input(key).lower()):
#						if not key in self.faulty:
#							self.faulty.append(key)
#							self.inputOK = False

#			if self.input(key) and fields[key] == str:
#				try:
#					_a = str(self.input(key))
#				except:
#					self.faulty.append(key)
#					self.inputOK = False

#			elif self.input(key) and fields[key] == unicode:
#				try:
#					_a = unicode(self.input(key))
#				except:
#					self.faulty.append(key)
#					self.inputOK = False


			try:
#				exec('_a = %s(self.input(key))' % (fields[key]))
				_a = fields[key](self.input(key))
			except:
				self.faulty.append(key)
				self.inputOK = False
			
			
#			if self.input(key) and fields[key] == int:
#				try:
#					_a = int(self.input(key))
#				except:
#					self.faulty.append(key)
#					self.inputOK = False
#
#			elif self.input(key) and fields[key] == float:
#				try:
#					_a = float(self.input(key))
#				except:
#					self.faulty.append(key)
#					self.inputOK = False

		# Process
#		for key in fields.keys():
#			if fields[key] == bool:
#				self.input(key)


		# REQUIRED
		self.requiredmissing = []
		for key in requiredfields:
			if key != None:
				if not self.input(key) or self.input(key) == '--empty--':
						if not key in self.requiredmissing:
							self.requiredmissing.append(key)
							self.inputOK = False
		
		self.inputFields = fields


class Response(object):
	
	responses = {
		'200': 'OK',
		'301': 'Redirect',
		'404': 'Not Found',
	}
	
	def __init__(self, parent, content = '', contentType = 'text/plain', responseCode = '200', header = None):
		self.parent = parent
		self.responseCode = str(responseCode)
		self.content = self.parent.smartString(content)
		self.contentType = contentType
		self.header = header

	def respond(self):
		
		self.parent.saveSession()

		responseList = []
		if self.content:
			responseList.append(('Content-type', self.contentType))
			responseList.append(('Content-Length', str(len(self.content))))

		if self.responseCode in self.responses:
			response = "%s %s" % (self.responseCode, self.responses[self.responseCode])
		else:
			response = str(self.responseCode)
	
		if self.header:
			responseList.append(self.header)
		
		# Send response
		self.parent.start_response(response, responseList)
		return self.content


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
			
			return path
		else:
			return 'No content'
		

######### SECURITY

def makeHash(string):
	u'''\
	Create hex hash string with SHA512.
	'''
	import hashlib
	return hashlib.sha512(string).hexdigest()
	