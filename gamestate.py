#!/usr/bin/env python
import os
import json
import sys
import cgi
import cgitb
import re
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
if not re.match("^[a-z0-9]+$", hand_id):
	print "Invalid hand ID."
	exit(0)
score = form.getfirst('score', 0)
try:
	score = int(score)
except Exception, e:
	score = 0

validating = False
if 'submit' in form:
	validating = True

f = open("hands/%s" % hand_id)

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
data = json.load(f)
#print data
hands = data['hands']
discards = data['discards']
# Until proper data mapping is available, everything is tsumokiri
for player in range(4):
	discards[player] = [(x,1) for x in discards[player]]
	discards[player] += [(-1, 0)] * (18 - len(discards[player]))
	# multiplying by negative gives []

calls = data['melds']
riichi = data['riichi']
riichi_tile = -1

#out = open("state.html", "w")
out = sys.stdout
out.write("""
<!DOCTYPE html>
<html><head>
<style type="text/css">
div {line-height: 0px;}
div#summary {line-height: 100% !important;}
div#toimen_hand {margin-left: 40px} /* enough to not overlap with kamicha_hand */
div#kamicha_hand {display: table-cell; vertical-align: middle; padding-right: 20px;}
div#kamicha_kawa {display: table-cell; vertical-align: middle; }
div#toimen_kawa {vertical-align: top; padding-bottom: 80px; text-align:
right; margin-left: 20px; margin-right: 20px}
div#own_kawa {vertical-align: bottom; padding-top: 80px; margin-left: 20px;
margin-right: 20px}
div#center_block {display: table-cell;vertical-align: middle} /* toimen_kawa, own_kawa, info block */
div#shimocha_kawa { display: table-cell;vertical-align: middle; }
div#shimocha_hand {display: table-cell;vertical-align: middle;padding-left: 20px;}
div#own_hand {display: table; margin-left: 40px;float: left;}
div#own_hand span {display: table-cell}
div#row {display: table-row;}
div.row {display: table-row;}
div.danger {background-color: red;}
td {padding: 0px}
img.tsumokiri, img.unselected {opacity: 0.60;}
img.danger_tile {border: 1px solid red;}
</style>
</head><body>\n""")
out.write("<div id='main'>\n")

def write_tile(tile, variant = ''):
	# This is annoying. Any space between the <img> tags spaces the images
	# in the output
	if tile[0] != -1:
		out.write("<img src='%s%s.png' />" %
				(tilelist[tile[0] / 4], variant))

# Top of the screen, show toimen first
out.write("<div id='toimen_hand'>\n")
# Calls not implemented yet since the test hand doesn't have any
for tile in reversed(hands[2]):
	if validating:
		write_tile((tile,), 'u')
	else:
		out.write("<img src='/images/back.png' />")
out.write("\n") # put a break between the blocks
toimen_called = [1, 2, 0, 0]
for call in reversed(calls[2]):
	for idx, tile in enumerate(call['tiles']):
		orientation = 'u'
		if idx == toimen_called[call['dealer']]:
			orientation = 'r'
		write_tile((tile,), orientation)
	out.write("\n")

out.write("</div>")
out.write("<div id='row'>\n")
# Left edge, player hand
out.write("<div id='kamicha_hand'>\n")
for tile in hands[3]:
	if validating:
		write_tile((tile,), 'l')
	else:
		out.write("<img src='/images/backl.png' />")
	out.write("<br />\n")

# kamicha calls... calls are tile is 2, 1, 0
# first tile is the one that was called, push it to the right place in the list
kamicha_called = [2,1,0]
# reversed because calls go outside to inside
for call in reversed(calls[3]):
	out.write("<br />\n")
	for idx, tile in enumerate(call['tiles']):
		orientation = 'l'
		if idx == kamicha_called[call['dealer']]:
			orientation = ''
		write_tile((tile,), orientation)
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
if riichi[3] > -1:
	riichi_tile = 2 - riichi[3]/6 + (x%6) * 3

for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		orientation = 'l'
		if y*3+x == riichi_tile:
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
riichi_tile = riichi[2]
append = ''
if data['player'] == 2:
	append = 'class="danger"'
out.write("<div id='toimen_kawa' %s >\n" % append)
while len(kawa) > 12:
	orientation = 'u'
	if len(kawa) == riichi_tile - 1:
		orientation = 'l'
	write_tile(kawa.pop(), orientation)
out.write("<br />\n")
while len(kawa) > 6:
	orientation = 'u'
	if len(kawa) == riichi_tile - 1:
		orientation = 'l'
	write_tile(kawa.pop(), orientation)
out.write("<br />\n")
while kawa:
	orientation = 'u'
	if len(kawa) == riichi_tile + 1:
		orientation = 'l'
	write_tile(kawa.pop(), orientation)

out.write("</div>\n") # toimen_kawa

# Own discards
kawa = discards[0]
out.write("<div id='own_kawa'>\n")
riichi_tile = riichi[0]
for i, tile in enumerate(kawa):
	orientation = ''
	if i == riichi_tile:
		orientation = 'r'
	write_tile(tile, orientation)
	if i > 4 and i < 18 and (i+1) % 6 == 0:
		out.write("<br />")
out.write("</div>") # own_kawa

out.write("</div>\n") # center_block

# Shimocha discards
append = ''
if data['player'] == 1:
	append = 'class="danger"'
out.write("<div id='shimocha_kawa' %s ><table>\n" % append)
# Similar arrangment to kamicha_discards
# Ignoring overflow for now...
kawa = [discards[1][5 - (i/3) + (i%3) * 6] for i in range(18)]
riichi_tile = -1
if riichi[1]> -1:
	riichi_tile = riichi[1] /6 + ((5 - riichi[1]%6) * 3)
for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		out.write("<td>")
		orientation = 'r'
		if riichi_tile == y*3+x:
			orientation = 'u'
		write_tile(kawa[y*3+x], orientation)
		out.write("</td>\n")
	out.write("</tr>\n")
out.write("</table></div>\n") # shimocha_kawa

# Another hand
out.write("<div id='shimocha_hand'>\n")
# [dealer number] -> tile position
shimocha_called = [2,0,0,1] # [1] is only used for kans
for call in calls[1]:
	for idx, tile in enumerate(reversed(call['tiles'])):
		orientation = 'r'
		if idx == shimocha_called[call['dealer']]:
			orientation = 'u'
		write_tile((tile,), orientation)
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
out.write("<input type='hidden' name='score' value='%d'></input>" % score)
out.write("<div id='own_hand'>\n")
out.write("<div class='row'>\n")
for i, tile in enumerate(hands[0]):
	classes = []
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
	for i, tile in enumerate(hands[0]):
		out.write("<span><input name='tile_%d' id='tile_%d' type='checkbox' /></span>\n" % (tile, i))
	out.write("<input type='submit' name='submit' value='Submit' />\n")

out.write("</div>\n") # row
out.write("</div></div>\n") # calls, own_hand
out.write("</form>\n")
# Insert called tiles around here
self_called = [0, 2, 1, 0]
for call in reversed(calls[0]):
	for idx, tile in enumerate(call['tiles']):
		orientation = ''
		if idx == self_called[call['dealer']]:
			orientation = 'r'
		write_tile((tile,), orientation)
	out.write("\n")

out.write("</div>\n") # main
if validating:
	out.write("<div id='summary' style='clear: left'>\n")
	out.write("<p>Full list of waits: \n")
	for tile in data['waits']:
		write_tile((tile * 4,))

	points = 0
	fail = False
	for key in form.keys():
		if key.find('tile_', 0, 5) == -1:
			continue
		tile = -1
		try:
			tile = int(key[5:])
		except Exception, e:
			continue
		if tile/4 in data['waits']:
			points = score = 0
			fail = True
			continue
		points += 1
	score += points
	if fail:
		out.write("</p><p>Dealt in. Score reset.")
	out.write("</p><p>Points this hand: %d<br />Total score: %d</p>" % (points,
			score))
	out.write("</p>\n")
	out.write("<form action='/cgi-bin/start.py' method='post'>\n")
	out.write("<input type='hidden' name='score' value='%d'></input>" % score)
	out.write("<input type='submit' name='next' value='Next hand'></input>\n")
	out.write("</form></div>\n")
out.write("</html>\n")
out.close()

