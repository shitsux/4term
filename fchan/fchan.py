#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


THUMB = "https://t.4cdn.org/%s/%is.jpg" # board name, image timestamp
IMG = "https://i.4cdn.org/%s/%i%s" # board name, image timesptamp, extension


class Post:
	comment = ""
	subject = ""
	user = None
	n_replies = None
	n_images = None

	def __init__(self, board=None):
		self.board = board

	def getTime(self):
		if self.time:
			return datetime.fromtimestamp(self.time)
		else:
			return None

	def getTokenizedComment(self):
		if self.comment:
			p = PostTokenizer()
			p.feed(self.comment)
			return p.parsed
		else:
			return []

class User:
	def __init__(self, name=None, email=None, trip=None, capcode=None):
		self.name = name
		self.email = email
		self.trip = trip
		self.capcode = capcode # none, mod, admin, admin_highlight, developer

class File:
	# TODO deleted files, spoiler
	def __init__(self, board, rename, ext, name, dim, thumb_dim, size, md5):
		self.board = board
		self.rename = rename
		self.ext = ext
		self.name = name
		self.dim = dim
		self.thumb_dim = thumb_dim
		self.size = size
		self.md5 = md5

	@property
	def thumb_url(self):
		return THUMB % (self.board, self.rename)

	@property
	def url(self):
		return IMG % (self.board, self.rename, self.ext)


class PostTokenizer(HTMLParser):
	"""
	Parse the few bits of html in a 4chan comment
	"""
	def __init__(self):
		HTMLParser.__init__(self)
		self.parsed = []

	def handle_starttag(self, tag, attrs):
		# TODO: spoilers, code, ???
		attrs = dict(attrs)
		if tag == "span":# and attrs[0] == ("class", "quote"):
			self.parsed.append(("QUOTE",))
		# TODO: internal links
		elif tag == "a":
			self.parsed.append(("LINK", attrs["href"]))
		elif tag == "i":
			self.parsed.append(("I",))
		elif tag == "br":
			self.parsed.append(("BR",))
	
	def handle_endtag(self, tag):
		if tag == "span":
			self.parsed.append(("QUOTE_END",))
		elif tag == "i":
			self.parsed.append(("I_END",))
		elif tag == "a":
			self.parsed.append(("LINK_END",))

	def handle_data(self, data):
		self.parsed.append(data)

	def handle_charref(self, name):
		if name.startswith('x'):
			self.parsed.append(unichr(int(name[1:], 16)))
		else:
			self.parsed.append(unichr(int(name)))

	def handle_entityref(self, name):
		self.parsed.append(unichr(name2codepoint[name]))
