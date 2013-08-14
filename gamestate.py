#!/usr/bin/env python
# coding=utf-8

# Build a HTML page showing a game state. Format is the JSON output from extract_hands.

import os
import json
import sys
import cgi
import cgitb
import re
import tenhou
import bz2
import zipfile
import subprocess
cgitb.enable()

# CGI blobby stuff
print "Content-Type: text/html;charset=utf-8"
print

form = cgi.FieldStorage()

if 'hand' not in form:
	print "hand ID required"
	# Should dump the user back to landing page
	exit(0)

hand_id = form.getfirst('hand')
if not re.match("^[a-z0-9-]+$", hand_id):
	print "Invalid hand ID."
	exit(0)
score = form.getfirst('score', 0)
try:
	score = int(score)
except Exception, e:
	score = 0

hand_count = form.getfirst('hands', 0)
try:
	hand_count = int(hand_count)
except Exception, e:
	hand_count = 0

validating = False
if 'submit' in form:
	validating = True

#f = open("hands/%s" % hand_id)
#smallblob = bz2.BZ2File("hands.zip.bz2")
#blob = zipfile.ZipFile("hands.zip")
#f = blob.open("hands/%s" % hand_id)

unblob = subprocess.check_output(["tar", "Oxf", "hands.tar.gz", "hands/%s" % hand_id])

data = json.loads(unblob)

# Lifted from paifu and probably gui
tilelist = []
for x in range(0, 9):
        tilelist.append("/images/%sm" % (x+1))
for x in range(0, 9):
        tilelist.append("/images/%sp" % (x+1))
for x in range(0, 9):
        tilelist.append("/images/%ss" % (x+1))
for x in range(0, 8):
        tilelist.append("/images/%sz" % (x+1))
# Stick .png on the end, as well as an orientation (l,r,u)

# Test for rendering a game state as a HTML page
# Hands ordered as in tenhou data - self, right, across, left
# (tile, tsumokiri?)
# f = open(sys.argv[1])
#print data
hands = data['hands']
discards = data['discards']
# Until proper data mapping is available, everything is tsumokiri
for player in range(4):
	# Shove this back into the usual format
	discards[player] = [(x%1024,x/1024) for x in discards[player]]
	discards[player] += [(-1, 0)] * (18 - len(discards[player]))
	# multiplying by negative gives []

calls = data['melds']
riichi = data['riichi']

#out = open("state.html", "w")
out = sys.stdout
out.write("""
<!DOCTYPE html>
<html><head>
<style type="text/css">
div {line-height: 0px;}
div#data_box {line-height: 150% !important; text-align: center;margin-top:
20px;margin-bottom: 20px}
table {border-collapse: collapse}
div#main {float: left;}
div#summary {line-height: 100% !important;}
div#toimen_hand {margin-left: 40px} /* enough to not overlap with kamicha_hand */
div#kamicha_hand {display: table-cell; vertical-align: middle; padding-right: 20px;}
div#kamicha_kawa {display: table-cell; vertical-align: middle; }
div#toimen_kawa {vertical-align: top; padding-bottom: 40px; padding-top: 10px; text-align:
right; margin-left: 20px; margin-right: 20px}
div#own_kawa {vertical-align: bottom; padding-top: 40px; margin-left: 20px;
margin-right: 20px; padding-bottom: 10px;}
div#center_block {display: table-cell;vertical-align: middle} /* toimen_kawa, own_kawa, info block */
div#shimocha_kawa { display: table-cell;vertical-align: middle; }
div#shimocha_hand {display: table-cell;vertical-align: middle;padding-left: 20px;}
div#own_hand {display: table; margin-left: 40px;float: left; overflow: visi}
div#own_hand span {display: table-cell}
div#own_calls {white-space: nowrap}
div#row {display: table-row;}
div.row {display: table-row;}
div.danger {background-color: red;}
td {border-spacing: 0px; padding: 0px; vertical-align: bottom}
td img {vertical-align: bottom; display: block;}
img.tsumokiri, img.unselected {opacity: 0.60}
div.called_bg {background-color: black; display: inline-block;}
div.called_bg img {opacity: 0.50;}
div.tsumokiri_bg {background-color: yellow; display: inline-block;}
div.tsumokiri_bg img {opacity: 0.80;}
img.danger_tile {border: 1px solid red;}
img.highlight_tile {border: 1px solid green}

</style>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js" type="text/Javascript"></script>
</head><body>\n""")
out.write("<div id='main'>\n")

def write_tile(tile, variant = '', ret = False):
	# This is annoying. Any space between the <img> tags spaces the images
	# in the output
	if tile[0] != -1:
		display = tile[0] / 4
		img = "<img src='%s%s.png' class='tile_%s' />" % \
				(tilelist[display], variant, display)
		if tile[1] & tenhou.DISCARD_CALLED:
			html = "<div class='called_bg'>%s</div>" % img
		elif tile[1] & tenhou.DISCARD_TSUMOKIRI:
			html = "<div class='tsumokiri_bg'>%s</div>" % img
		else:
			html = img
		if ret:
			return html
		else:
			out.write(html)

def write_back(variant = '', ret = False):
	if variant == 'u':
		variant = ''
	elif variant == 'r':
		variant = 'l'
	html = "<img src='/images/back%s.png' class='tile_back' />" % variant
	if ret:
		return html
	else:
		out.write(html)

#### toimen hand ####
out.write("<div id='toimen_hand'>\n")
# calls first
toimen_called = [1, 2, -1, 0]
for call in reversed(calls[2]):
	if len(call['tiles']) == 4 and call['dealer'] == 2:
		# minkan
		write_tile((call['tiles'][0],0), 'u')
		write_back()
		write_back()
		write_tile((call['tiles'][0],0), 'u')
	else:
		rotated = toimen_called[call['dealer']]
		if len(call['tiles']) == 4 and rotated == 2:
			rotated = 3
		for idx, tile in enumerate(reversed(call['tiles'])):
			orientation = 'u'
			if idx == rotated:
				orientation = 'r'
			write_tile((tile,0), orientation)
	out.write("\n")

for tile in reversed(hands[2]):
	if validating:
		write_tile((tile,0), 'u')
	else:
		out.write("<img src='/images/back.png' />")

out.write("</div>")
out.write("<div id='row'>\n")
# Left edge, player hand
out.write("<div id='kamicha_hand'>\n")
for tile in hands[3]:
	if validating:
		write_tile((tile,0), 'l')
	else:
		out.write("<img src='/images/backl.png' />")
	out.write("<br />\n")

# kamicha calls... calls are tile is 2, 1, 0
# first tile is the one that was called, push it to the right place in the list
kamicha_called = [2,1,0,-1]
# reversed because calls go outside to inside
for call in reversed(calls[3]):
	out.write("<br />\n")
	if len(call['tiles']) == 4 and call['dealer'] == 3:
		tiles = [write_tile((call['tiles'][0],0), 'l', True)]
		tiles.append(write_back('l', True))
		tiles.append(write_back('l', True))
		tiles.append(write_tile((call['tiles'][0],0), 'l', True))
		out.write(("<br />\n").join(tiles))
	else:
		rotated = kamicha_called[call['dealer']]
		if len(call['tiles']) == 4 and rotated == 2:
			rotated = 3
		for idx, tile in enumerate(call['tiles']):
			orientation = 'l'
			if idx == rotated:
				orientation = ''
			write_tile((tile,0), orientation)
			out.write("<br />\n")

out.write("</div>")

# In the middle, div for all the discards
# toimen discards in 3 rows

# first row: if at least 12 discards, <tile or blank>
# second row: " 6, <tile or blank>
# 3rd row: <tile or blank>
# blanks necessary for spacing
# or could div them out and float, same as the other rows...
# Generate a rotated array for the first 18 tiles
# Going to need to do something about overflowed hands later
kawa = [discards[3][(i/3) + (6 * (2 - (i%3)))] for i in range(18)]
# extend with all the rest
append = ''
if data['player'] == 3:
	append = 'class="danger"'
out.write("<div id='kamicha_kawa' %s ><table >\n" % append)
# Inverse of the transform above

for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		orientation = 'l'
		if kawa[y*3+x][1] & tenhou.DISCARD_RIICHI:
			orientation = ''
		out.write("<td>")
		write_tile(kawa[y*3+x], orientation)
		out.write("</td>\n")
	out.write("</tr>\n")
out.write("</table></div>\n")

out.write("<div id='center_block'>")
# Toimen discards
# transform is just reversed discards
kawa = discards[2]
append = ''
if data['player'] == 2:
	append = 'class="danger"'
out.write("<div id='toimen_kawa' %s >\n" % append)
while len(kawa) > 12:
	orientation = 'u'
	tile = kawa.pop()
	if tile[1] & tenhou.DISCARD_RIICHI:
		orientation = 'l'
	write_tile(tile, orientation)
out.write("<br />\n")
while len(kawa) > 6:
	orientation = 'u'
	tile = kawa.pop()
	if tile[1] & tenhou.DISCARD_RIICHI:
		orientation = 'l'
	write_tile(tile, orientation)
out.write("<br />\n")
while kawa:
	orientation = 'u'
	tile = kawa.pop()
	if tile[1] & tenhou.DISCARD_RIICHI:
		orientation = 'l'
	write_tile(tile, orientation)

out.write("</div>\n") # toimen_kawa

#### data box ####
out.write("<div id='data_box'>\n")
rounds = ['東1局', '東2局', '東3局', '東4局',
	'南1局','南2局','南3局','南4局',
	'西1局','西2局','西3局','西4局'] # tenhou stops here
#rounds = ['East 1', 'East 2', 'East 3', 'East 4', 'South 1', 'South 2', 'South 3',
#	'South 4', 'West 1', 'West 2', 'West 3', 'West 4']
#players = ['East', 'South', 'West', 'North'] # TODO: IME this once it's working again
players = ['東','南','西','北']

out.write("%s<br /><span style='margin-right: 2em;'>%s</span>\n" % (players[(2 - data['dealer']) % 4],
	players[(3 - data['dealer']) % 4]))
out.write("<span style='font-weight: bold;'>%s</span>\n" % rounds[data['round']])
out.write("<span style='margin-left: 2em;'>%s</span><br />%s" % 
		(players[(1 - data['dealer']) % 4],
		players[(0 - data['dealer']) % 4]))

out.write("</div>\n")

#### Own discards ####
kawa = discards[0]
out.write("<div id='own_kawa'>\n")
for i, tile in enumerate(kawa):
	orientation = ''
	# seeing own riichi makes it easy to find the danger tile
	#if tile[1] & tenhou.DISCARD_RIICHI:
	#	orientation = 'r'
	write_tile(tile, orientation)
	if i > 4 and i < 18 and (i+1) % 6 == 0:
		out.write("<br />")
out.write("</div>") # own_kawa

out.write("</div>\n") # center_block

#### Shimocha discards ####
append = ''
if data['player'] == 1:
	append = 'class="danger"'
out.write("<div id='shimocha_kawa' %s ><table>\n" % append)
# Similar arrangment to kamicha_discards
# Ignoring overflow for now...
kawa = [discards[1][5 - (i/3) + (i%3) * 6] for i in range(18)]
for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		out.write("<td>")
		orientation = 'r'
		if kawa[y*3+x][1] & tenhou.DISCARD_RIICHI:
			orientation = 'u'
		write_tile(kawa[y*3+x], orientation)
		out.write("</td>\n")
	out.write("</tr>\n")
out.write("</table></div>\n") # shimocha_kawa

# Another hand
out.write("<div id='shimocha_hand'>\n")
# [dealer number] -> tile position
shimocha_called = [2,-1,0,1]
for call in calls[1]:

	if len(call['tiles']) == 4 and call['dealer'] == 1:
		tiles = [write_tile((call['tiles'][0],0), 'r', True)]
		tiles.append(write_back('r', True))
		tiles.append(write_back('r', True))
		tiles.append(write_tile((call['tiles'][0],0), 'r', True))
		out.write(("<br />\n").join(tiles))
	else:
		rotated = shimocha_called[call['dealer']]
		if len(call['tiles']) == 4 and rotated == 2:
			rotated = 3

		for idx, tile in enumerate(reversed(call['tiles'])):
			orientation = 'r'
			if idx == rotated:
				orientation = 'u'
			write_tile((tile,0), orientation)
			out.write("<br />")

	out.write("<br />")

for tile in reversed(hands[1]):
	if validating:
		out.write("<img src='%sr.png' /><br />\n" % tilelist[tile / 4])
	else:
		out.write("<img src='/images/backl.png' /><br />\n")
out.write("</div>")
out.write("</div>") # row

# Final hand
out.write("<form method='post' action='/cgi-bin/gamestate.py'>\n")
out.write("<input type='hidden' name='hand' value='%s'></input>\n" % hand_id)
out.write("<input type='hidden' name='hands' value='%s'></input>\n" % hands)
out.write("<input type='hidden' name='score' value='%d'></input>" % score)
out.write("<div id='own_hand'>\n")
out.write("<div class='row'>\n")
for i, tile in enumerate(sorted(hands[0])):
	classes = ['tile_%s' % (tile / 4)]
	if validating and 'tile_%d' % tile not in form:
		classes.append('unselected')
	if validating and tile/4 in data['waits']:
		classes.append('danger_tile')

	if classes:
		append = 'class="%s"' % ' '.join(classes)
	else:
		append = ''
	out.write("<span><label for='tile_%d'><img %s src='%s.png' /></label></span>\n"
			% (i, append, tilelist[tile / 4]))
out.write("</div><div class='row'>\n")
if not validating:
	for i, tile in enumerate(sorted(hands[0])):
		out.write("<span><input name='tile_%d' id='tile_%d' type='checkbox' on/></span>\n" % (tile, i))
	out.write("<input type='submit' name='submit' value='Submit' />\n")

out.write("</div>\n") # row
out.write("</div>\n") # own_hand
out.write("</form>\n")
#### own called tiles ####
out.write("<div id='own_calls'>\n")
self_called = [-1, 2, 1, 0]
for call in reversed(calls[0]):
	if len(call['tiles']) == 4 and call['dealer'] == 0:
		# minkan
		write_tile((call['tiles'][0],0))
		write_back()
		write_back()
		write_tile((call['tiles'][0],0))
	else:
		rotated = self_called[call['dealer']]
		if rotated == 2 and len(call['tiles']) == 4:
			rotated = 3
		for idx, tile in enumerate(call['tiles']):
			orientation = ''
			if idx == rotated:
				orientation = 'r'
			write_tile((tile,0), orientation)
	out.write("\n")
out.write("</div>\n") # own_calls
out.write("</div>\n") # main

dora = ["<img src='%s.png' />" % tilelist[t/4] for t in data['dora']]
out.write("""<div id='outside_data'>Dora indicators: %s</div>""" % ''.join(dora))
if validating:
	out.write("<div id='summary' style='clear: left'>\n")
	out.write("<p>Full list of waits: \n")
	for tile in data['waits']:
		write_tile((tile * 4,0))

	points = 0
	fail = False
	oldscore = score
	oldhands = hand_count
	hand_count += 1
	for key in form.keys():
		if key.find('tile_', 0, 5) == -1:
			continue
		tile = -1
		try:
			tile = int(key[5:])
		except Exception, e:
			continue
		if tile/4 in data['waits']:
			points = score = hand_count = 0
			fail = True
			break
		points += 1
	score += points
	if fail:
		out.write("</p><p>Dealt in. Score reset. Score: %d Hands: %d" %
				(oldscore, oldhands))
	out.write("</p><p>Points this hand: %d<br />Total score: %d<br />Hands: %d</p>" % (points,
		score, hand_count))
	out.write("</p>\n")
	out.write("<form action='/cgi-bin/start.py' method='post'>\n")
	out.write("<input type='hidden' name='score' value='%d'></input>" % score)
	out.write("<input type='hidden' name='hands' value='%d'></input>" %
			hand_count)
	out.write("<input type='submit' name='next' value='Next hand'></input>\n")
	out.write("</form></div>\n")
out.write("<p style='clear: left;'><br />Hand ID: <a href='/cgi-bin/gamestate.py?hand=%s'>%s</a></p>\n"
		% (hand_id, hand_id))
out.write("""
<script type="text/Javascript">
/* incomplete
$("img[class*='tile_']").hover(
	function(){$(this).addClass("highlight_tile");},
	function(){$(this).removeClass("highlight_tile");});
*/
</script>
</body></html>""")

out.close()
