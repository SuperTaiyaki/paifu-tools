#!/usr/bin/env python
import os

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
hands = [[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
	[30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
	[50, 55, 52, 53, 54, 55, 56, 57, 58, 59, 60, 65, 62],
	[70, 77, 72, 73, 74, 75, 76, 77, 78, 79, 80, 87, 82]]
discards = [[1,2,3,4,5,6,7,8],[3,4,5, 113, 114, 115, 116, 117],[6,7,8],[100, 101, 102, 103, 104, 105, 106, 107,
	108, 109, 110, 111, 112]]
for player in range(4):
	discards[player] = [(x,1) for x in discards[player]]
	discards[player] += [(-1, 0)] * (18 - len(discards[player]))
	# multiplying by negative gives []
print discards

calls = [[], [], [], []]
riichi = [-1, -1, -1, -1]

out = open("state.html", "w")
out.write("""
<!DOCTYPE html>
<html><head>
<style type="text/css">
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
img.tsumokiri {opacity: 0.75;}
</style>
</head><body>\n""")
out.write("<div id='main'>\n")
# Top of the screen, show toimen first
out.write("<div id='toimen_hand'>\n")
for tile in hands[2]:
	out.write("<img src='%su.gif' />\n" % tilelist[tile / 4])
out.write("</div>")
out.write("<div id='row'>\n")
# Left edge, player hand
out.write("<div id='kamicha_hand'>\n")
for tile in hands[3]:
	out.write("<img src='%sl.gif' /><br />\n" % tilelist[tile / 4])
out.write("</div>")

# In the middle, div for all the discards
# toimen discards in 3 rows

# first row: if at least 12 discards, <tile or blank>
# second row: " 6, <tile or blank>
# 3rd row: <tile or blank>
# blanks necessary for spacing
# or could div them out and float, same as the other rows...
# Generate a rotated array for the first 18 tiles

def write_tile(tile, variant = ''):
	if tile[0] == -1:
		out.write("<td></td>\n")
	else:
		out.write("<td><img src='%s%s.gif' /></td>\n" %
				(tilelist[tile[0] / 4], variant))

# Going to need to do something about overflowed hands later
kawa = [discards[3][(i/3) + (6 * (2 - (i%3)))] for i in range(18)]
# extend with all the rest
out.write("<div id='kamicha_kawa'><table >\n")
for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		write_tile(kawa[y*3+x], 'l')
	out.write("</tr>\n")
out.write("</table></div>\n")

out.write("<div id='center_block'>")
# Toimen discards
# transform is just reversed discards
kawa = discards[2]
out.write("<div id='toimen_kawa'>\n")
while len(kawa) > 12:
	write_tile(kawa.pop(), 'u')
out.write("<br />\n")
while len(kawa) > 6:
	write_tile(kawa.pop(), 'u')
out.write("<br />\n")
while kawa:
	write_tile(kawa.pop(), 'u')

out.write("</div>\n") # toimen_kawa

# Own discards
kawa = discards[0]
out.write("<div id='own_kawa'>\n")
for i, tile in enumerate(kawa):
	write_tile(tile)
	if i > 0 and i < 18 and i % 6 == 0:
		out.write("<br />")
out.write("</div>") # own_kawa

out.write("</div>\n") # center_block

# Shimocha discards
out.write("<div id='shimocha_discards'><table>\n")
# Similar arrangment to kamicha_discards
# Ignoring overflow for now...
kawa = [discards[1][5 - (i/3) + (i%3) * 6] for i in range(18)]
for y in range(6):
	out.write("<tr>\n")
	for x in range(3):
		write_tile(kawa[y*3+x], 'r')
	out.write("</tr>\n")
out.write("</table></div>\n") # shimocha_discards

# Another hand
out.write("<div id='shimocha_hand'>\n")
for tile in hands[1]:
	out.write("<img src='%sr.gif' /><br />\n" % tilelist[tile / 4])
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
out.write("</div>\n") # own_hand
out.write("</form>\n")

out.write("</div>\n") # main
out.write("</html>")
out.close()

