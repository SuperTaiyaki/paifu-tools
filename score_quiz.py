#!/usr/bin/python

import tenhou
import random

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
			if start > 26 or start % 9 > 7:
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
	print tenhou._count_score(calls, tiles, 0, 0, tsumo, final_tile)

#print(generate_tiles())
generate_hand()

