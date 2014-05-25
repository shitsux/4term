#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Access to the 4chan JSON API
"""

import json
from urllib2 import urlopen, HTTPError

from fchan import Post, File, User


INDEX = "https://a.4cdn.org/%s/%i.json" # board name, pagenumber
CAT = "https://a.4cdn.org/%s/catalog.json" # board name
THREAD = "https://a.4cdn.org/%s/thread/%i.json" # board name, thread id


def getPageFromCatalog(board, page=0):
	try:
		page = json.load(urlopen(CAT % board))
	except HTTPError, e:
		raise Exception("\"%s\" doesn't exist. Specified board likely to be incorrect" % (CAT % board))
	if page not in range(0, len(page)):
		raise Exception("Page \"%i\" doesn't exist" % page)

	for thread in page[page]['threads']:
		yield JsonOP(board, thread)

def getThread(board, thread):
	try:
		page = json.load(urlopen(THREAD % (board, thread)))
	except HTTPError, e:
		raise Exception("\"%s\" doesn't exist. Board or thread (must be OP!) likely to be incorrect" % (THREAD % (board, thread)))
	for post in page['posts']:
		yield JsonPost(board, post)


class JsonPost(Post):
	def __init__(self, board, json):
		self.board = board
		self.json = json

	@property
	def id(self):
		return self.json['no']

	@property
	def ftime(self):
		"""
		Pre-formatted time
		"""
		return self.json['now']

	@property
	def time(self):
		""" 
		UNIX timestamp
		"""
		return self.json['time']

	@property
	def reply_to(self):
		return self.json['resto']

	@property
	def subject(self):
		if 'sub' in self.json:
			return self.json['sub']
		else:
			return None

	@property
	def comment(self):
		if 'com' in self.json:
			return self.json['com']
		else:
			return None

	@property
	def file(self):
		if 'tim' in self.json:
			return File(self.board,
				self.json['tim'],
				self.json['ext'],
				self.json['filename'],
				(self.json['w'], self.json['h']),
				(self.json['tn_w'], self.json['tn_h']),
				self.json['fsize'],
				self.json['md5'])
		else:
			return None

	@property
	def user(self):
		props = {}
		for key in ('name', 'email', 'trip', 'capcode'):
			if key in self.json:
				props[key] = self.json[key]
		return User(**props)

class JsonOP(JsonPost):
	reply_to = 0

	#TODO custom spoiler, omitted posts,images, bump, image limit, semantic url
	@property
	def is_sticky(self):
		return 'sticky' in self.json

	@property
	def is_closed(self):
		return 'closed' in self.json

	@property
	def n_replies(self):
		return self.json['replies']

	@property
	def n_images(self):
		return self.json['images']

	@property
	def last_replies(self):
		return (JsonPost(x) for x in self.json['last_replies']) 
