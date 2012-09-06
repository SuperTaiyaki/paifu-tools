#!/usr/bin/env python

import glob
import random
import cgi
import cgitb
import zipfile
import bz2
import tarfile
import subprocess
cgitb.enable()

#files = glob.glob("hands/*")
# Yes this is stupid. But so is the zip format - it doesn't compress between
# files. The tarfile module doesn't allow streaming out single files.
#smallblob = bz2.BZ2File("hands.zip.bz2")
#blob = zipfile.ZipFile("hands.zip")
#blob = tarfile.open("hands.tar.bz2")
#hand = random.choice(blob.getnames())
hands = subprocess.check_output(["tar", "tf", "hands.tar.gz"]).splitlines()
hand = random.choice(hands)

#hand = 'hands/hand1346582280164'
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

print 'Status: 200 OK' # This seems to make the browser hide the real URL... good for hiding the score
print 'Content-Type: text/plain'
print 'Location: %s' % target
print
# Should put a HTML redirect here
