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

initial_hands = [list(player.hand) for player in game.players]
if game.event != 'draw':
	print "ERROR: First event isn't a draw! NFI what's going on. Event: %s" % game.event
	exit
initial_hands[game.player].append(game.tile)
draws[game.player].append(TILE_BLANK)
# Wonder if there's a cleaner way to do this...
map(lambda x: x.sort(), initial_hands)

# Main loop goes here
# Waiting for 'deal' doesn't work - there needs to be a trigger on agari, to
# capture finishing hands
while game.event != 'deal':
	game = iter.next()
	if game.event == 'draw':
		draws[game.player].append(game.tile)
	elif game.event == 'discard':
		discards[game.player].append(game.tile)
		if discards[game.player][-1] == draws[game.player][-1]:
			draws[game.player][-1] = TILE_ARROW

output("""<html>
<head></head>
<body>""")

for player in range(0,4):
	output("Initial hand: ")
	for tile in initial_hands[player]:
		output('<img src="%s" />\n' % tile_image(tile))
	output("<br />Draws: ")
	for tile in draws[player]:
		output('<img src="%s" />\n' % tile_image(tile))
	output("<br />Discards: ")
	for tile in discards[player]:
		output('<img src="%s" />\n' % tile_image(tile))


	output("<hr />\n")

output("""</body></html>""")

