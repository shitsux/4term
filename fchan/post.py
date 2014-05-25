#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Posting to 4chan
"""

import re
from urllib import urlencode
from urllib2 import urlopen, Request

import http
from recaptcha import ReCaptcha


BOARD = "http://boards.4chan.org/%s/" # board name
THREAD = "http://boards.4chan.org/%s/thread/%s" # board name, thread id
POST = "https://sys.4chan.org/%s/post"
# let's blame the botnet
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1517.3 Safari/537.36'


RE_MAXSIZE = re.compile(
			r'<input type="hidden" name="MAX_FILE_SIZE" value="([0-9]+)">')
RE_POSTERROR = re.compile(
			'<span id="errmsg"[^>]*>([^<]+)</span>')


class Poster:
	"""
	Post on 4chan through simple web scraping
	"""

	data = { 'mode' : 'regist',
			'submit' : 'Post'}

	def __init__(self, board, post, thread=None, pwd="", filename=None):
		if thread: 
			self.ref = THREAD % (board, thread)
			self.data['resto'] = str(thread)
		else:
			self.ref = BOARD % board

		self.board = board
		self.file = filename
		self.data['com'] = post.comment
		if post.user:
			self.data['name'] = post.user.name
			self.data['email'] = post.user.email

		#self.data['sub'] = post.subject
		self.data['pwd'] = pwd
		# spoiler?

	def fetch(self):
		"""
		Fetches page to finalize initialization and the CAPTCHA question
		"""
		page = urlopen(self.ref).read()
		self.data['MAX_FILE_SIZE'] = RE_MAXSIZE.search(page).group(1)
		self.captcha = ReCaptcha(page)
		self.captcha.fetch()

	def post(self):
		"""
		Completes posting
		CAPTCHA must be solved at this point

		raises Exception, when 4chan doesn't accept your post
		"""

		self.data.update(self.captcha.getData())

		form = http.MultiPartForm()
		for k,v in self.data.iteritems():
			form.add_field(k, v)

		if self.file:
			form.add_file('upfile', self.file, open(file, 'r'))

		request = Request(POST % self.board)

		request.add_header('User-agent', USER_AGENT)
		request.add_header('Referer', self.ref) 

		body = str(form)
		request.add_header('Content-type', form.get_content_type())
		request.add_header('Content-length', len(body))
		request.add_data(body)
	
		response = urlopen(request).read()
		err =  RE_POSTERROR.search(response)
		if err:
			raise Exception("4chan says: "+err.group(1))
