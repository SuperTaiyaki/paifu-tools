#!/usr/bin/env python

import glob
import random
import cgi
import cgitb
cgitb.enable()

files = glob.glob("hands/*")
hand = random.choice(files)
form = cgi.FieldStorage()
score = form.getfirst('score', 0)
try:
	score = int(score)
except Exception, e:
	score = 0
target = '/cgi-bin/gamestate.py?hand=%s' % hand[6:]
if score:
	target += '&score=%d' % score

print 'Content-Type: text/plain'
print 'Location: %s' % target
print