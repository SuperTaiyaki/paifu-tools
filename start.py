#!/usr/bin/env python

import glob
import random
import cgi
import cgitb
import zipfile
import bz2
cgitb.enable()

#files = glob.glob("hands/*")
# Yes this is stupid. But so is the zip format - it doesn't compress between
# files. The tarfile module doesn't allow streaming out single files.
#smallblob = bz2.BZ2File("hands.zip.bz2")
blob = zipfile.ZipFile("hands.zip")
hand = random.choice(blob.infolist()).filename
# maybe filter out empty files?
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
