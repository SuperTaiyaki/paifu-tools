#!/usr/bin/python2

import tenhou
import random
import sys

out = sys.stdout
tilelist = []
for x in range(0, 9):
        tilelist.append("images/%sm" % (x+1))
for x in range(0, 9):
        tilelist.append("images/%sp" % (x+1))
for x in range(0, 9):
        tilelist.append("images/%ss" % (x+1))
for x in range(0, 8):
        tilelist.append("images/%sz" % (x+1))


# Try generating a random hand - 1-34 representation
def generate_tiles():
	# chiitoitsu, kokushi, etc...

	# Probably needs to generate special hands too - ikki, chinitsu...

	tiles = [4] * 34
	parts = []
	# This is not going to return a correct distribution, but it should be good enough
	while len(parts) < 4:
		if random.randrange(10) < 6: # Weight towards mentsu
			# Mentsu
			start = random.randrange(34)
			# Can't start on 8 or 9, can't be terminal
			if start > 26 or start % 9 > 6:
				continue
			if not all(tiles[start:start+3]):
				continue
			tiles[start] -= 1 # Feels like this can be streamlined...
			tiles[start+1] -= 1
			tiles[start+2] -= 1
			parts.append([start, start+1, start+2])
			continue
		else:
			start = random.randrange(34)
			if tiles[start] < 3:
				continue
			tiles[start] -= 3
			parts.append([start, start, start])
	# Add in the pair
	pair = random.randrange(34)
	while tiles[pair] < 2:
		pair = random.randrange(34)
	parts.append([pair, pair])
	return parts

def generate_hand():
	tiles = generate_tiles()
	calls = []
	riichi = False
	called = False
	tsumo = random.randrange(2) # Final tile only

	type = random.randrange(11)
	if type < 3:
		riichi = True
	elif type < 6:
		pass
	elif type < 9:
		called = True
	else:
		# chiitoitsu
		pass
	print(type)

	if called:
		for group in tiles:
			if len(group) == 2:
				continue
			call = {}
			call['tiles'] = group
			if tiles[0] == tiles[1]:
				call['type'] = 'pon'
			else:
				call['type'] = 'chi'
			calls.append(call)
			tiles.remove(group)
			# Is the rest irrelevant?

	final_group_no = random.randrange(len(tiles))
	final_group = tiles[final_group_no]
	# del tiles[final_group_no]
	final_tile = random.choice(final_group)
	# final_group.remove(final_tile)

	print(tiles)
	print(calls)
	print("Final tile: %s" % final_tile)

	#fu = tenhou._count_fu(calls, tiles, 0, 0, tsumo, final_tile)
	#print(fu)
	print(tenhou._count_score(calls, tiles, 0, 0, tsumo, final_tile))

	# Rendering only from here
	# Flatten out the tiles
	tiles = [x for y in tiles for x in y]
	tiles.remove(final_tile)
	render_hand(tiles, [], final_tile)

def write_tile(tile, variant = '', ret = False):
	# This is annoying. Any space between the <img> tags spaces the images
	# in the output
	if tile != -1:
		display = tile
		img = "<img src='%s%s.png' class='tile_%s' />" % \
			(tilelist[display], variant, display)
		out.write(img)

def render_hand(tiles, calls, final):
	out.write("""
<!DOCTYPE html>
<html><head>
<style type="text/css">
div {line-height: 0px;}
div#data_box {line-height: 150% !important; text-align: center;margin-top:
20px;margin-bottom: 20px}
table {border-collapse: collapse}
td {border-spacing: 0px; padding: 0px; vertical-align: bottom}
td img {vertical-align: bottom; display: block;}

</style>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js" type="text/Javascript"></script>
</head><body>

	""")

	out.write("<br />\n")
	for tile in tiles:
		write_tile(tile)

	out.write("Final: ")
	write_tile(final)

	out.write("""</body></html>""")

#print(generate_tiles())
generate_hand()

