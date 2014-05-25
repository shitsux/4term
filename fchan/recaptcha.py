#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from urllib import urlencode
from urllib2 import urlopen

# TODO: look if ReCaptcha has some kind of API

RE_FRAME = re.compile(
		r'<iframe src="//([^"]+)"')
RE_CHALLENGE = re.compile(
			r'<input type="hidden" name="recaptcha_challenge_field" id="recaptcha_challenge_field" value="([^"]+)">')
RE_ANSWER = re.compile(
			r'<textarea rows="5" cols="100">([^<]+)</textarea>')
IMAGE = "http://www.google.com/recaptcha/api/image?c=%s"


class ReCaptcha:
	key = None

	def __init__(self, page):
		self.frame_url = 'http://' + RE_FRAME.search(page).group(1)

	def _getChallenge(self, frame):
		self.challenge = RE_CHALLENGE.search(frame).group(1)

	def fetch(self):
		"""
		Fetches a (new) CAPTCHA question
		"""
		self._getChallenge(urlopen(self.frame_url).read())

	def getData(self):
		"""
		Returns dictionary with the generated key
		  ready to urlencoded and send with ReCaptcha-using forms
		"""
		# TODO: Might be that only 4chan uses these form names
 
		if self.key:
			return {'recaptcha_challenge_field' : self.key,
				'recaptcha_response_field' : 'manual_challenge'}
		else:
			raise Exception("CAPTCHA not solved yet")

	def getImage(self):
		"""
		Returns URL of image to be solved
		"""
		return IMAGE % self.challenge

	def solve(self, solution):
		"""
		Posts solution
		
		return True for correct solution and key becomes available
		returns False if the solution is wrong and gets ready to solve another
		"""
		data = { 'recaptcha_challenge_field' : self.challenge,
					'recaptcha_response_field' : solution,
					'submit' : "I'm a human"}
		page = urlopen(self.frame_url, urlencode(data)).read()	
		key = RE_ANSWER.search(page)
		if key:
			self.key = key.group(1)
			return True
		else:
			self._getChallenge(page)
			return False
