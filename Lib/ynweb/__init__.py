# -*- coding: utf-8 -*-

import cgi, os, re, http.cookies, datetime


class YNWeb(object):
	def __init__(self, environ, start_response):
		self.environ = environ
		self.start_response = start_response
		self.inputFields = {}
		self.fileObjects = {}
		self.transmitHeaders = []
		
		try:
			self.session = self.environ['beaker.session']
		except:
			self.session = None
		self.sessionaltered = False


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

		if 'HTTP_USER_AGENT' in self.environ:

		
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
			


	def apacheLog(self, what):
		print(what, file=self.environ['wsgi.errors'])

		
	# INPUT
	def input(self, key):
		import urllib.request, urllib.parse, urllib.error
		
		if hasattr(self, 'form') and key in self.form:
			
			if key in self.inputFields:
				if self.inputFields[key] == bool:
					value = self.form.getfirst(key)
				
					if value == 'True' or value == 'true' or value == '1' or value == 'on':
						return True
					elif value == 'False' or value == 'false' or value == '0' or value == '':
						return False
				
				elif self.inputFields[key] == int:
					return int(self.form.getfirst(key))

				elif self.inputFields[key] == str:
					return urllib.parse.unquote(self.form.getfirst(key))

				elif self.inputFields[key] == 'file':
					return self.form.getfirst(key)

				else:
					return urllib.parse.unquote(self.form.getfirst(key))
			else:
				try:
					return urllib.parse.unquote(self.form.getfirst(key))
				except:
					return self.form.getfirst(key)
		else:
			return ''
			#urllib.unquote(url).decode('utf8')

	def file(self, key):
		if key in self.form and hasattr(self.form[key], 'file'):
			
#			if self.form[key].filename:

			if key not in self.fileObjects:
				self.fileObjects[key] = UploadFile(self.form[key].filename, self.form[key].file.read())
			
			return self.fileObjects[key]

	def response(self, content = '', contentType = 'text/plain', responseCode = '200', header = None):
		return Response(self, content, contentType, responseCode, header)

	def redirect(self, url):
		return Response(self, responseCode = '301', header = ('Location', url))

	def fail(self):
		return Response(self, responseCode = '500')

	def saveSession(self):
		if self.session:
			if self.sessionaltered:
				self.session.save()
				

	# SESSION
	def getSession(self, key):
		if self.session:
			if key in self.session:
				return self.session[key]

	def setSession(self, key, value):
		if self.session:
			self.session[key] = value
			self.sessionaltered = True


	# COOKIES
	def getCookie(self, key):
		value = None
		if 'HTTP_COOKIE' in self.environ:
			cookie = http.cookies.SimpleCookie()
			cookie.load(self.environ['HTTP_COOKIE'])
			if key in cookie:
			 	value = cookie[key].value
		return value

	def setCookie(self, key, value):
		cookie = http.cookies.SimpleCookie()
		cookie[key] = value
		cookie[key]["path"] = "/"
		expires = datetime.datetime.utcnow() + datetime.timedelta(days=10*365) # expires in 10 years
		cookie[key]['expires'] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
		self.transmitHeaders.append(('Set-Cookie',cookie[key].OutputString()))

	def deleteCookie(self, key):
		cookie = http.cookies.SimpleCookie()
		cookie[key] = ''
		cookie[key]["path"] = "/"
		cookie[key]['expires'] = 'Thu, 01 Jan 1970', '00:00:00 GMT'
		self.transmitHeaders.append(('Set-Cookie',cookie[key].OutputString()))


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
		for key in list(fields.keys()):
			

			try:
#				exec('_a = %s(self.input(key))' % (fields[key]))
				_a = fields[key](self.input(key))
			except:
				self.faulty.append(key)
				self.inputOK = False



		# REQUIRED
		self.requiredmissing = []
		for key in requiredfields:
			if key != None:
				if not self.input(key) or self.input(key) == '__empty__' or self.input(key) == 'undefined':
						if not key in self.requiredmissing:
							self.requiredmissing.append(key)
							self.inputOK = False
		


		self.inputFields = fields


class Response(object):
	
	responses = {
		'100': 'Continue',
		'101': 'Switching Protocols',
		'102': 'Processing',
		'200': 'OK',
		'201': 'Created',
		'202': 'Accepted',
		'203': 'Non-authoritative Information',
		'204': 'No Content',
		'205': 'Reset Content',
		'206': 'Partial Content',
		'207': 'Multi-Status',
		'208': 'Already Reported',
		'226': 'IM Used',
		'300': 'Multiple Choices',
		'301': 'Moved Permanently',
		'302': 'Found',
		'303': 'See Other',
		'304': 'Not Modified',
		'305': 'Use Proxy',
		'307': 'Temporary Redirect',
		'308': 'Permanent Redirect',
		'400': 'Bad Request',
		'401': 'Unauthorized',
		'402': 'Payment Required',
		'403': 'Forbidden',
		'404': 'Not Found',
		'405': 'Method Not Allowed',
		'406': 'Not Acceptable',
		'407': 'Proxy Authentication Required',
		'408': 'Request Timeout',
		'409': 'Conflict',
		'410': 'Gone',
		'411': 'Length Required',
		'412': 'Precondition Failed',
		'413': 'Payload Too Large',
		'414': 'Request-URI Too Long',
		'415': 'Unsupported Media Type',
		'416': 'Requested Range Not Satisfiable',
		'417': 'Expectation Failed',
		'418': 'I’m a teapot',
		'421': 'Misdirected Request',
		'422': 'Unprocessable Entity',
		'423': 'Locked',
		'424': 'Failed Dependency',
		'426': 'Upgrade Required',
		'428': 'Precondition Required',
		'429': 'Too Many Requests',
		'431': 'Request Header Fields Too Large',
		'444': 'Connection Closed Without Response',
		'451': 'Unavailable For Legal Reasons',
		'499': 'Client Closed Request',
		'500': 'Internal Server Error',
		'501': 'Not Implemented',
		'502': 'Bad Gateway',
		'503': 'Service Unavailable',
		'504': 'Gateway Timeout',
		'505': 'HTTP Version Not Supported',
		'506': 'Variant Also Negotiates',
		'507': 'Insufficient Storage',
		'508': 'Loop Detected',
		'510': 'Not Extended',
		'511': 'Network Authentication Required',
		'599': 'Network Connect Timeout Error',
	}
	
	def __init__(self, parent, content = '', contentType = 'text/plain', responseCode = '200', header = None):
		self.parent = parent
		self.responseCode = str(responseCode)
		self.content = content
		self.contentType = contentType
		self.header = header

	def respond(self):
		
#		content = bytes(self.content, 'utf-8')
#		content = self.content

#		self.parent.apacheLog(str(type(self.content)))

		try:
			content = str.encode(self.content)
		except:
			content = bytes(self.content)

#		self.parent.apacheLog(str(type(content)))
		# self.parent.apacheLog(self.content)

		self.parent.saveSession()

		if self.responseCode != '200' and self.content == '':
			self.content = "%s %s" % (self.responseCode, self.responses[self.responseCode])

		responseList = []
		if self.content:
			responseList.append(('Content-type', self.contentType))
			responseList.append(('Content-Length', str(len(content))))

		if self.responseCode in self.responses:
			response = "%s %s" % (self.responseCode, self.responses[self.responseCode])
		else:
			response = self.responseCode
	
		if self.header:
			responseList.append(self.header)

		if self.parent.transmitHeaders:
			for header in self.parent.transmitHeaders:
				responseList.append(header)
			self.parent.transmitHeaders = []
			
		# Close MySQL connection
#		if self.parent.db:
#			self.parent.db.disconnect()

		# Send response
		self.parent.start_response(response, responseList)
		return [content]


class UploadFile(object):
	def __init__(self, filename, content):
		self.filename = filename
		self.content = content
		if self.filename:
			self.ending = self.filename.lower().split('.')[-1]
		self.size = len(self.content)

	def save(self, folder, filename = None):
		if self.content:
			
			try:
				os.makedirs(folder)
			except:
				pass
			
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
	'''\
	Create hex hash string with SHA512.
	'''
	import hashlib
	return hashlib.sha512(string).hexdigest()
	