#!/usr/bin/env python
import os
import json
import sys

# Lifted from paifu and probably gui
tilelist = []
for x in range(0, 9):
        tilelist.append("images/%sm" % (x+1))
for x in range(0, 9):
        tilelist.append("images/%sp" % (x+1))
for x in range(0, 9):
        tilelist.append("images/%ss" % (x+1))
for x in range(0, 8):
        tilelist.append("images/%sz" % (x+1))
# Stick .gif on the end, as well as an orientation (l,r,u)


# Test for rendering a game state as a HTML page
# Junk data for now...
# Hands ordered as in tenhou data - self, right, across, left
# (tile, tsumokiri?)
f = open(sys.argv[1])
data = json.load(f)
print data
hands = [[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
	[30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
	[50, 55, 52, 53, 54, 55, 56, 57, 58, 59, 60, 65, 62],
	[70, 77, 72, 73, 74, 75, 76, 77, 78, 79, 80, 87, 82]]
discards = [[1,2,3,4,5,6,7,8],[3,4,5, 113, 114, 115, 116, 117],[6,7,8],[100, 101, 102, 103, 104, 105, 106, 107,
	108, 109, 110, 111, 112]]

hands = data['hands']
discards = data['discards']
for player in range(4):
	discards[player] = [(x,1) for x in discards[player]]
	discards[player] += [(-1, 0)] * (18 - len(discards[player]))
	# multiplying by negative gives []

calls = [[], [], [], []]
calls = data['melds']
riichi = [4, 4, 1, 4]
riichi = data['riichi']
riichi_tile = -1

out = open("state.html", "w")
out.write("""
<!DOCTYPE html>
<html><head>
<style type="text/css">
div {line-height: 0px;}
div#toimen_hand {}
div#kamicha_hand {display: table-cell; vertical-align: middle}
div#kamicha_kawa {display: table-cell; vertical-align: middle}
div#toimen_kawa {vertical-align: top; padding-bottom: 25%; text-align:
right}
div#own_kawa {vertical-align: bottom; padding-top: 25%}
div#center_block {display: table-cell;vertical-align: middle} /* toimen_kawa, own_kawa, info block */
div#shimocha_discards { display: table-cell;vertical-align: middle}
div#shimocha_hand {display: table-cell;vertical-align: middle;}
div#own_hand {display: table}
div#own_hand span {display: table-cell}
div#row {display: table-row;}
div.row {display: table-row;}
td {padding: 0px}
img.tsumokiri {opacity: 0.75;}
</style>
</head><body>\n""")
out.write("<div id='main'>\n")

def write_tile(tile, variant = ''):
	if tile[0] != -1:
		out.write("<img src='%s%s.gif' />" %
				(tilelist[tile[0] / 4], variant))

# Top of the screen, show toimen first
out.write("<div id='toimen_hand'>\n")
# Calls not implemented yet since the test hand doesn't have any
for tile in reversed(hands[2]):
	#write_tile((tile,), 'u')
	# This is annoying. Any space between the <img> tags spaces the images
	# in the output
	out.write("<img src='images/back.gif' />")
out.write("</div>")
out.write("<div id='row'>\n")
# Left edge, player hand
out.write("<div id='kamicha_hand'>\n")
for tile in hands[3]:
	#write_tile((tile,), 'l')
	out.write("<img src='images/backl.gif' />")
	out.write("<br />\n")

# kamicha calls... calls are tile is 2, 1, 0
# first tile is the one that was called, push it to the right place in the list
kamicha_called = [2,1,0]
# reversed because calls go outside to inside
for call in reversed(calls[3]):
	print call
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
out.write("<div id='kamicha_kawa'><table >\n")
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
out.write("<div id='toimen_kawa'>\n")
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
out.write("<div id='shimocha_discards'><table>\n")
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
out.write("</table></div>\n") # shimocha_discards

# Another hand
out.write("<div id='shimocha_hand'>\n")
# [dealer number] -> tile position
shimocha_called = [2,0,0,1] # [1] is only used for kans
for call in calls[1]:
	print call
	for idx, tile in enumerate(reversed(call['tiles'])):
		orientation = 'r'
		if idx == shimocha_called[call['dealer']]:
			orientation = 'u'
		write_tile((tile,), orientation)
		out.write("<br />")

	out.write("<br />")

for tile in reversed(hands[1]):
	#out.write("<img src='%sr.gif' /><br />\n" % tilelist[tile / 4])
	out.write("<img src='images/backl.gif' /><br />\n")
out.write("</div>")
out.write("</div>") # row

# Final hand
out.write("<form method='post'>\n")
out.write("<div id='own_hand'>\n")
out.write("<div class='row'>\n")
for i, tile in enumerate(hands[0]):
	out.write("<span><label for='tile_%d'><img src='%s.gif' /></label></span>\n"
			% (i, tilelist[tile / 4]))
out.write("</div><div class='row'>\n")
for i, tile in enumerate(hands[0]):
	out.write("<span><input name='tile_%d' id='tile_%d' type='checkbox' /></span>\n" % (tile, i))
	# Temporary test, put in images instead of checkboxes
	#out.write("<img src='%s.gif' />\n" % tilelist[tile / 4])
out.write("<input type='submit' name='submit' value='Submit' />\n")
out.write("</div>") # row
# Insert called tiles around here
out.write("</div>\n") # own_hand
out.write("</form>\n")

out.write("</div>\n") # main
out.write("</html>")
out.close()

