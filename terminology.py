#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for Terminology
"""

import sys, re
import fcntl, termios, struct

# basic ANSI/xterm escape codes
TERM_SGR = "\033[%sm"
TERM_FG = TERM_SGR % "38;5;%i"
TERM_BG = TERM_SGR % "48;5;%i"

TERM_COL = {
		"green" : 2,
		"blue" : 4,
		"grey" : 8,
		"qgreen" : 112
		}

# Terminology image escape codes
TERMI_ESC = "\033}%s\000"
# zoom ((s)tretch, (c)enter, (f)ill, (t)humbnail),
# replacement character, width, height,
# path/url (or "link\npath-or-url" for zoom=t)
TERMI_I = TERMI_ESC % "i%s%s%i;%i;%s"
TERMI_SEQ = TERMI_ESC % "ib" + "%s" + TERMI_ESC % "ie"

RE_ESCAPES = re.compile(r'\033((\[[^m]*m)|(\}[^\000]*\000))')

def getSize():
	"""
	Get terminal dimension
	"""
	h, w, hp, wp = struct.unpack('HHHH',
	fcntl.ioctl(0, termios.TIOCGWINSZ,
	struct.pack('HHHH', 0, 0, 0, 0)))
	return w, h

def resetColor():
	return TERM_SGR % "0"

def changeColor(fg=None, bg=None):
	ret = ""
	if fg:
		if isinstance(fg, str):
			fg = TERM_COL[fg]
		ret = TERM_FG % fg
	else:
		if isinstance(bg, str):
			bg = TERM_COL[bg]
		ret += TERM_BG % bg
	return ret

def colorize(text, fg=None, bg=None):
	return changeColor(fg, bg) + text + resetColor()

def startItalic():
	return TERM_SGR % 3

def stopItalic():
	return TERM_SGR % 23

def loadImage(zoom, placeholder, w, h, path, link=None):
	"""
	Loads an image and returns appropiate placeholder
	"""
	if link:
		
		if zoom != "t":
			raise "Can only use links for thumbnails"
		else:
			# quick hack because terminology seems to fail
			# to display urls as thumb when you use links
			import urllib, tempfile, os
			if path.startswith("http"):
				f, fpath = tempfile.mkstemp(prefix="/tmp/term/")
				with os.fdopen(f, "w") as f:
					f.write(urllib.urlopen(path).read())
				path = fpath
				
			sys.stdout.write(TERMI_I
					% (zoom, placeholder, w, h, link + "\n" + path))
	else:
		sys.stdout.write(TERMI_I % (zoom, placeholder, w, h, path))

	return tuple(TERMI_SEQ % (placeholder * w) for x in range(0,h))


def wrap(text, max):
	"""
	Dumb word wrap that ignores escape codes
	"""

	ret = ""
	for line in text.splitlines():
		offset = 0
		for i in RE_ESCAPES.finditer(line):
			offset += i.span()[1] - i.span()[0]
		start = 0
		end = max + offset
		while end < len(line):
			ns = line.rfind(' ', start, end)
			if ns > -1:
				ret += line[start:ns]+'\n'
				start = ns
				end += start+1
			else:
				ret += line[start:end]+'\n'
				start = end
				end = start + max + offset
		ret += line[start:] + '\n'
	return ret
