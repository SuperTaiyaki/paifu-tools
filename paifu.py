import sys
import tenhou

tilelist = []
for x in range(0, 9):
#        tilelist.append(Image(source="%sm.gif" % (x+1)))
        tilelist.append("images/%sm.gif" % (x+1))
for x in range(0, 9):
#        tilelist.append(Image(source="%sp.gif" % (x+1)))
        tilelist.append("images/%sp.gif" % (x+1))
for x in range(0, 9):
#        tilelist.append(Image(source="%ss.gif" % (x+1)))
        tilelist.append("images/%ss.gif" % (x+1))
for x in range(0, 8):
#        tilelist.append(Image(source="%sz.gif" % (x+1)))
        tilelist.append("images/%sz.gif" % (x+1))
img_arrow = "images/arrow.gif"
img_blank = "images/blank.gif"

TILE_ARROW = -2
TILE_BLANK = -1

def tile_image(tile):
	# Handle red 5s
	# 4, 13, 22?

	if tile == TILE_ARROW:
		return img_arrow
	elif tile == TILE_BLANK:
		return img_blank
	else:
		return tilelist[tile / 4]

# Don't mix in all the debug noise from the tenhou module
f = open("paifu.html", "w")

def output(x):
	f.write(x)

iter = tenhou.run_log(sys.stdin)
iter.next() # Start the game
game = iter.next()

draws = [[], [], [], []]
discards = [[], [], [], []]
events = [[], [], [], []]

initial_hands = [list(player.hand) for player in game.players]
player = -1
if game.event != 'draw':
	print "ERROR: First event isn't a draw! NFI what's going on. Event: %s" % game.event
	exit
initial_hands[game.player].append(game.tile)
draws[game.player].append(TILE_BLANK)
player = game.player
# Wonder if there's a cleaner way to do this...
map(lambda x: x.sort(), initial_hands)

def fill_blanks(new_player):
	global player
	player = (player + 1) % 4
	while player != new_player:
		print "Stuffing blank into player %s" % player
		draws[player].append(TILE_BLANK)
		discards[player].append(TILE_BLANK)
		player = (player + 1) % 4

# Main loop goes here
# Waiting for 'deal' doesn't work - there needs to be a trigger on agari, to
# capture finishing hands
while game.event != 'deal':
	game = iter.next()
	print "Player: %s" % player
	if game.event == 'draw':
		draws[game.player].append(game.tile)
		player = game.player
	elif game.event == 'discard':
		discards[game.player].append(game.tile)
		if discards[game.player][-1] == draws[game.player][-1]:
			draws[game.player][-1] = TILE_ARROW
		player = game.player
	elif game.event == 'pon' or game.event == 'chi' or game.event == 'kan':
		print "Previous player: %s" % player
		print "Event player: %s" % game.player
		fill_blanks(game.player)
		player = game.player
		draws[game.player].append(game.tile)
		print game.tile
		print ("Tile %s attached to player %s's draws" %
			(tenhou.tile_decode(game.tile), game.player))



output("""<html>
<head></head>
<body>
<table>""")
for player in range(0,4):
	output("<tr>")
	output("<td>Initial hand:</td><td> ")
	for tile in initial_hands[player]:
		output('<img src="%s" />\n' % tile_image(tile))
	output("</td></tr><td>Draws: </td><td>")
	for tile in draws[player]:
		output('<img src="%s" />\n' % tile_image(tile))
	output("</td></tr><tr><td>Discards:</td><td>")
	for tile in discards[player]:
		output('<img src="%s" />\n' % tile_image(tile))

	output("</td></tr><tr><td colspan='2'><hr /></td></tr>\n")

output("""</table></body></html>""")

