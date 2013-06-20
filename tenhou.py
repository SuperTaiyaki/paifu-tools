#!/usr/bin/python

import copy
import sys
import itertools
from xml.dom.minidom import parse

DISCARD_TSUMOKIRI = 1
DISCARD_CALLED = 2
DISCARD_RIICHI = 4

#>>> tenhou.convert_tiles([x*4 for x in [0,8,9,17,18,26,27,28,29,30,31,32,33]])
#['1m', '9m', '1p', '9p', '1s', '9s', 'ton', 'nan', 'sha', 'pei', 'haku', 'hatsu', 'chun']
 
TERMINALS = set([0,8,9,17,18,26,27,28,29,30,31,32,33])
HONOURS = set([27,28,29,30,31,32,33])

def debug(args):
	#print(args)
	pass

# Friendlier tile representation
def tile_decode(tile):
	tile /= 4
	if tile < 0:
		return 'error'
	if tile < 9:
		return "%sm" % (tile + 1)
	elif tile < 18:
		return "%sp" % (tile - 8)
	elif tile < 27:
		return "%ss" % (tile - 17)
	elif tile == 27:
		return "ton"
	elif tile == 28:
		return "nan"
	elif tile == 29:
		return "sha"
	elif tile == 30:
		return "pei"
	elif tile == 31:
		return "haku"
	elif tile == 32:
		return "hatsu"
	elif tile == 33:
		return "chun"
	return "Invalid tile"

def convert_tiles(tiles):
	return [tile_decode(t) for t in tiles]


def read_tiles(string):
	""" Take a shorthand hand representation and return an array of tile numbers."""
	tiles = []
	ret = []
	suits = 'mpsz'
	for c in string:
		if c in suits:
			offset = suits.index(c)*9
			ret.extend([offset+x for x in tiles])
			tiles = []
		else:
			# Human representation is 1-based
			tiles.append(int(c) - 1)
	return ret

# Take out all complete mentsu
def reduce(tiles):
	# transform to tiles[tile #] = (count of tile)
	tc = [0] * 34
	mentsu = 0
	for tile in tiles:
		tc[tile] += 1

	for i in range(28, 34): # honours first, all koutsu
		if tc[i] >= 3:
			tc[i] -= 3
			mentsu += 1

	# Cut out the rest of the koutsu

	# Cut out the shuntsu
	for base in [0, 9, 18]:
		for inc in range(7):
			while all([tc[base+inc+i] for i in range(3)]):
				tc[base+inc] -= 1
				tc[base+inc+1] -= 1
				tc[base+inc+2] -= 1

	# convert the remainder back to the original representation
	output = []
	for tile, count in enumerate(tc):
		output.extend([tile] * count)
	return output

# Tiles is an array of tile indices, not tile counts
def chiitoitsu(tiles):
	if len(tiles) != 14:
		return False
	s = sorted(tiles)
	# Assuming they don't have to be distinct pairs. TODO: confirm for
	# Tenhou
	return all((s[i] == s[i + 1] for i in range(0,14,2)))


def kokushi(tiles):
	terminals = set([0,8,9,17,18,26,27,28,29,30,31,32,33])
	hand = set(tiles)
	remainder = terminals - hand
	# TODO: NYI
	return False


# The _reduce functions, but with (shuntsu, return) signatures
def _gather_koutsu(tiles):
	for tile in range(len(tiles)):
		if tiles[tile] >= 3:
			out = copy.copy(tiles)
			out[tile] -= 3
			yield ((tile, tile, tile), out)
def _gather_mentsu(tiles):
	for base in [0, 9, 18]:
		for inc in range(7):
			if all([tiles[base+inc+i] for i in [0,1,2]]):
				out = copy.copy(tiles)
				out[base+inc] -= 1
				out[base+inc+1] -= 1
				out[base+inc+2] -= 1
				yield ((base+inc, base+inc+1, base+inc+2), out)

# Alternative chiitoitsu, using the 34-array of tiles
def _chiitoitsu(tiles):
	# Is this making any incorrect assumptions? The concern is that there
	# will be tiles with 1 or 3 available and the kantsu will stuff the hand
	# up to 14 anyway
	# Probably not a problem as kantsu will knock the number of incoming
	# tiles below 14.
	return tiles.count(2) + tiles.count(4) * 2 == 7

def _kokushi(tiles):
	if tiles.count(2) != 1 and tiles.count(1) != 12:
		return False
	for tile in TERMINALS:
		if not tiles[tile]:
			return False
	return True

# Yes/no check only
def _agari(tiles):
	# No tiles left
	if max(tiles) == 0:
		return False
	# If there's only a pair left, we're done
	if tiles.count(2) == 1 and sum(tiles) == 2:
		return True

	iter = itertools.chain(_gather_koutsu(tiles), _gather_mentsu(tiles))
	if any((_agari(hand) for _, hand in iter)):
		return True
	return False

# In: melds, list of tiles
# Out: [] of hands
# hand is [(melds)]
def _agari_structures(parts, tiles):
	# No tiles left
	if _kokushi(tiles):
		# unique, no need to do any further processing
		pass
	elif _chiitoitsu(tiles):
		pass
		# chiitoitsu requires all 14 tiles, so recursive calls will fall
		# short
	if max(tiles) == 0:
		return []
	# If there's only a pair left, we're done
	if tiles.count(2) == 1 and sum(tiles) == 2:
		tile = tiles.index(2)
		return [sorted(parts + [(tile, tile)])]

	structures = []
	iter = itertools.chain(_gather_koutsu(tiles), _gather_mentsu(tiles))
	for meld, tiles in iter:
		ret = _agari_structures(parts + [meld], tiles)
		# Rather than checking for dupes, something with strict ordering
		# may work better
		for hand in ret:
			if hand not in structures:
				structures.append(hand)

	return structures

# tiles 0-34, not 0-136
def agari(hand):
	# chiitoitsu, kokushi
	if len(hand) == 14:
		if chiitoitsu(hand) or kokushi(hand):
			return True

	tc = [0] * 34
	mentsu = 0
	for tile in hand:
		tc[tile] += 1
	return _agari(tc)

# Return all valid interpretations of the partial hand
def agari_structures(hand):
	tc = [0] * 34
	mentsu = 0
	for tile in hand:
		tc[tile] += 1
	return _agari_structures([], tc)

# Need to pass in how the last tile was obtained...
def yaku(calls, tiles, round):
	parts = agari_structure(tiles)

# tsumo = self drawn winning tile, regardless of hand structure
# round is 0-11 for east 1 - west 4
# seat is 0 for east 1st dealer
# tsumo is t/f
# Hand should _include_ final_tile
def _count_fu(calls, hand, round, seat, tsumo, final_tile):
	fu_list = [(20, 'base')]
	fu = 20
	if not tsumo and not calls:
		fu += 10
		fu_list.append((10, 'menzen ron'))
	if tsumo: # Hrm, need to account for pinfu... probably
		fu += 2
		fu_list.append((2, 'tsumo'))
	for call in calls:
		cf = 2
		if call['type'] == 'chi':
			continue
		elif call['type'] == 'kan':
			cf *= 4
			# Do something about closed kan here - double again
		tile = call['tiles'][0]
		if tile in TERMINALS:
			cf *= 2
		fu += cf
		if cf:
			fu_list.append((cf, 'call %s' % str(call)))
	# Wait check
	# TODO NYI
	# Two-sided wait if a group in hand
	#- Contains the tile at an extremity (i.e. not position [1])
	#- doesn't also contain a terminal

	ryanmen = False
	for group in hand:
		if final_tile in group:
			if len(group) == 2:
				continue
			if group[0] == group[1]:
				continue
			if group[1] == final_tile:
				continue # kanchan
			# Penchan is a pain...
			if (final_tile % 9 == 2 and group[0] % 9 == 0) or\
				(final_tile % 9 == 6 and group[2]%9 == 8):
				continue
			ryanmen = True
			break
	if not ryanmen:
		fu += 2
		fu_list.append((2, 'wait'))

	for meld in hand:
		if len(meld) == 2:
			# Pair check
			tile = meld[0]
			# round wind
			if tile == round + 27:
				# Check!
				fu += 2
				fu_list.append((2, 'Round wind pair'))
			# self wind - not exclusive!
			if tile == seat + 27:
				fu += 2
				fu_list.append((2, 'Self wind pair'))
			# dragons
			if tile > 30:
				fu += 2
				fu_list.append((2, 'Dragon pair'))
			continue
		if meld[0] != meld[1]:
			continue # mentsu
		tile = meld[0]

		cf = 4 # 2 base, 2 closed
		if tile in TERMINALS:
			cf *= 2
		# kans become calls
		fu += cf
		fu_list.append((cf, 'Structure bonus: %s' % str(meld)))
	print(fu_list)
	return fu
	# Probably worth breaking up the result too

# Later, will need a function to go through the entire list and sort out any
# conflicts (toitoi/suuankou etc)

# These functions assume the hand is not chiitoitsu or kokushi

# Check for tanyao, honroutou, chinroutou, tsuiisou
# non-structural
def _yaku_terminals(tiles):
	terminals = 0
	middles = 0
	honours = 0

	for tile in tiles:
		if tile in HONOURS:
			honours += 1

		if tile in TERMINALS: # Yes, implies the above
			terminals += 1
		else:
			middles += 1
	print("Terminals: %d Middles: %d Honours: %d" % (terminals, middles, honours))
	if middles != 0 and terminals != 0:
		return [] # Nothing interesting
	if terminals == 0:
		return [('tanyao', 1)]
	elif honours == 14:
		return [('tsuiisou', 13)]
	elif honours == 0:
		return [('chinroutou', 13)]
	else:
		return [('honroutou', 2)]

def _yaku_ryuuiisou(tiles):
	# 23468s, hatsu
	greens = [19, 20, 21, 23, 25, 32]
	for x in tiles:
		if x not in greens:
			return []
	return [('ryuuiisou', 13)]

# Honitsu, Chinitsu
# non-structural (mostly)
def _yaku_suit(tiles):
	suits = [0,0,0,0] # manzu, pinzu, souzu, honours... but it doesn't actually matter much
	for tile in tiles:
		suits[tile / 9] += 1
	if suits[0:2].count(0) < 2:
		return []
	if suits[3] == 0:
		return [('chinitsu', 6)] # TODO: do something about kuisagari
		# Also, check for chuuren here?
	else:
		return [('honitsu', 3)] # also kuisagari

def _yaku_chanta(calls, melds):
	open = False
	for meld in calls:
		open = True
		# Is this going to mess up the original object?
		melds += meld['tiles']
	# Could also check junchan
	#if all(lambda y: any(lambda x: x in TERMINALS, y), melds):
		# So apparently, True and False work as 1 and 0
	#	return [('chanta', 1 + open)]
	return []

def _yaku_itsuu(calls, melds):
	open = False
	all_melds = melds + [call.tiles for call in calls]
	all_melds.sort()
	# Ugh, delete out the pair somehow...

	for start in 0, 1:
		if all_melds[start][0] % 9 != 0:
			continue
		for x in range(3):
			if all_melds[x][0] == all_melds[x][1]:
				continue # mentsu OR PAIR
		if all_melds[start][0] + 3 == all_melds[start+1][0] and\
				all_melds[start][0] + 6 == all_melds[start+2][0]:
					# kuisagari
					return [('ittsuu', 1 + 0)]
	return []

def _yaku_yakuhai(calls, melds, round, seat):
	yakuhai = [31, 32, 33] # dragons
	yakuhai.extend(round+27)
	yakuhai.extend(seat+27)

	# Non-yakuhai stuff gets mixed in, but it doesn't matter
	tiles = [x[0] for x in calls + melds]

	yaku = 0
	# Loop this way to catch double winds
	for tile in yakuhai:
		if group[0] in tiles:
			yaku += 1

	return [('yakuhai', 1)] * yaku

def _yaku_kans(calls, melds, seat, tsumo):
	if not calls:
		return []
	kans = 0
	for call in calls:
		if call.type == kan:
			kans += 1
	if kans == 3:
		return [('sankantsu', 2)]
	elif kans == 4:
		return [('suukantsu', 4)]

# final_tile is ???
# tsumo is true/false
def _count_score(calls, melds, round_wind, seat_wind, tsumo, final_tile):
	yaku = []
	if not calls and tsumo:
		yaku.append(('menzen', 1))

	fu = _count_fu(calls, melds, round_wind, seat_wind, tsumo, final_tile)

	if tsumo and fu == 22 and not calls:
		yaku.append(('pinfu', 1))
	elif not tsumo and fu == 30 and not calls:
		yaku.append(('pinfu', 1))

	# Squish the data down to the list of tiles only
	tiles = []
	map(lambda x: tiles.extend(x['tiles']), calls)
	map(lambda x: tiles.extend(x), melds)
	# tanyao tsuuiisou chinroutou honroutou
	yaku.extend(_yaku_terminals(tiles))
	# ryuuiisou
	yaku.extend(_yaku_ryuuiisou(tiles))
	# chinitsu honitsu
	yaku.extend(_yaku_suit(tiles))

	# chanta
	yaku.extend(_yaku_chanta(calls, melds))
	# itsuu
	yaku.extend(_yaku_itsuu(calls, melds))

	return yaku

# Brute force-ish method, try each tile and see if it completes the hand
# This ignores tiles that are impossible (i.e. held in a kan or by opponents)
# Could possibly be optimized by ignoring empty suits, but that requires some
# trickery to catch kokushi
def agari_tiles(hand):
	outs = []
	for tile in range(34):
		if agari(hand + [tile]):
			outs.append(tile)
	return outs

def shanten(hand):
	# ignoring chiitoitsu for now
	suits = [[],[],[],[]]
	for tile in hand:
		if tile < 9*4:
			suits[0].append(tile)
		elif tile < 18*4:
			suits[1].append(tile)
		elif tile < 27*4:
			suits[2].append(tile)
		else:
			suits[3].append(tile)


class Player(object):
	def __init__(self):
		self.hand = set() # implicit ordering?
		self.tsumo = None
		self.melds = []
		self.draws = []
		self.discards = [] # ordered
		self.riichitile = None
		self.called = set()

	def draw(self, tiles):
		self.hand = set()
		for x in tiles:
			self.hand.add(x)

	def draw1(self, tile):
		self.tsumo = tile

	def discard(self, tile):
		debug("Hand before: %s" % (map(tile_decode,list(self.hand))))
		if tile in self.hand:
			self.hand.remove(tile)
			# after a call this could be None
			# 1m is 0, don't let this fail
			if self.tsumo is not None:
				self.hand.add(self.tsumo)
		# if not in the hand, it must be the tsumo
		flag = 0
		if self.tsumo == tile:
			flag = DISCARD_TSUMOKIRI
		self.discards.append((tile, flag))
		self.tsumo = None
		debug("Hand after: %s" % (map(tile_decode,list(self.hand))))

	def riichi(self):
		self.riichitile = self.discards[-1][0]
		(tile, flag) = self.discards[-1]
		flag |= DISCARD_RIICHI
		self.discards[-1] = (tile, flag)

	# stuff for calls

	def call(self, call):
		for t in call['tiles']:
			self.hand.discard(t)
		#debug("Processed call, new hand: ")
		#debug(self.hand)
		self.melds.append(call)

	# Mark the last discard as being called by someone else
	def mark_called(self):
		self.called.add(self.discards[-1])
		(tile, flag) = self.discards[-1]
		flag |= DISCARD_CALLED
		self.discards[-1] = (tile, flag)

class Game(object):
	def __init__(self, dealer = 0, round = 0):
		self.players = [Player(), Player(), Player(), Player()]

		self.wall = []

		# Basically re-interpreting the log events...
		self.event = ''
		self.tile = -1
		self.player = -1
		self.data = {} # Miscellaneous crap holding for events
		self.dealer = dealer
		self.round = round
		self.dora = []

	# wall generation NYI, too complicated

	def deal(self, players):
		for i in range(0,4):
			self.players[i].draw(players[i])
		self.event = 'deal'
		self.tile = -1
		self.player = -1
	def draw(self, player, tile):
		self.players[player].draw1(tile)
		self.event = 'draw'
		self.tile = tile
		self.player = player
	def discard(self, player, tile):
		self.players[player].discard(tile)
		self.event = 'discard'
		self.tile = tile
		self.player = player
	def riichi(self, player):
		self.players[player].riichi()
		self.event = 'riichi'
		self.tile = self.players[player].riichitile
		self.player = player
	def call(self, player, data):
		self.players[player].call(data)
		# The 'dealer' element of the call is relative to the caller,
		# not the client. Push it around a bit.
		dealer = (data['dealer'] + player) % 4
		data['dealer'] = dealer # the relative value isn't useful
		self.players[dealer].mark_called()
		#self.event = 'call' # TODO: indicate what the call is
		self.event = data['type']
		self.tile = data['tiles'][data['called']]
		self.player = player
	def add_dora(self, tile):
		self.dora.append(tile) # indicators or actual tiles? not sure yet.
	# Set up arbitrary events for things like ryuukyoku that don't change
	# the game state
	def set_event(self, event, player = -1, tile = -1, other = {}):
		self.event = event
		self.tile = tile
		self.player = player
		self.data = other

def parse_call(code):
	# python struct only supports bytes, not bits
	# Test call: 45577, pon west
	#	= type 89, tile 116 + (1,2,3) (= west - so it works...)
	# 57423 = chi, 567s (called the 7 from player to the left - player 1?)
	#	= 0xe04f
	#	= 0b1110000001001111
	# 48745 = pon haku
	# 42537 = pon east
	# 46335 = chi 234s (called 2)
	# 29935 = chi 345p (called 5p)
	debug("Dealing with call %d = %x" % (code, code))
	call = {}
	# branching based on the JS sample code
	if code & (1 << 2):
		# chi. also matches nuki, but ignoring 3ma
		call['dealer'] = code & 0x3
		base = (code >> 10) & 0x3f
		bn = (((base/3)/7)*9+((base/3)%7))*4
		tile1 = (code >> 3) & 0x3
		tile2 = ((code >> 5) & 0x3) + 4
		tile3 = ((code >> 7) & 0x3) + 8
		# actual tile that got called is base % 3
		call['called'] = base % 3
		# Order so that the called tile is at the front
		if call['called'] == 0:
			call['tiles'] = (bn + tile1, bn + tile2, bn + tile3)
		elif call['called'] == 1:
			call['tiles'] = (bn + tile2, bn + tile1, bn + tile3)
		elif call['called'] == 2:
			call['tiles'] = (bn + tile3, bn + tile1, bn + tile2)

		call['type'] = 'chi'

		debug("Chi: %s %s %s" % call['tiles'])
	elif code & (1 << 3): # 0b111 xx = 0b010 xx
		debug("Pon")
		call['dealer'] = code & 0x3 # this is _relative to the caller_
		unused = (code >> 5) & 0x3 # the tile not in the meld
		tiles = code >> 9
		call['called'] = tiles % 3
		base = (tiles / 3) * 4

		call['tiles'] = []
		for i in range (0,4):
			if i == unused:
				continue
			call['tiles'].append(base + i)
		call['type'] = 'pon'
	elif code & (1 << 4):
		# chakan - extending a koutsu
		# will need support logic in player to handle this
		pass
	elif code & (1 << 5):
		# nuki, NFA
		return {}
	else:
		# other kan
		debug("Kan")
		# kan
		tile = code >> 8
		call['called'] = tile % 4
		tile &= ~3 # mask out the called bits
		call['tiles'] = range(tile, tile+4)
		call['dealer'] = code & 0x3
		call['type'] = 'kan'
	# Should put an exception here
	return call


draw_cmd = ['T', 'U', 'V', 'W'] # self, right, opposite, left
discard_cmd = ['D', 'E', 'F', 'G']
ignore_cmd = ['SHUFFLE', 'TAIKYOKU', 'UN', '#text'] # #text is a weird xml thing?

def run_log(stream):
	doc = parse(stream)

	gamelog = doc.firstChild # mjloggm
	game = None
	riichi = False
	for element in gamelog.childNodes:
		#debug("Node: " + element.nodeName)
		#debug("Value: " + str(element.nodeValue))

		if element.nodeName in ignore_cmd:
			continue
		elif element.nodeName == 'GO':
			gametype = int(element.attributes['type'].value)
			if gametype & 0x10:
				print "3p not supported."
				raise StopIteration
			continue
		elif element.nodeName == 'INIT':

			seed = element.attributes['seed'].value.split(',')
			# round, honba, leftover riichi sticks, die1, die2, dora
			round = int(seed[0])
			dora = int(seed[5])
			dealer = int(element.attributes['oya'].value)

			game = Game(round = round, dealer = dealer)
			game.add_dora(dora)
			hands = []
			for x in range(0,4):
				hand = element.attributes['hai%s' % x].value
				tiles = hand.split(",")
				tiles = [int(x) for x in tiles]
				hands.append(tiles)
			debug("HANDS STARTED: %s" % (hands))
			game.deal(hands)
		elif element.nodeName == 'DORA':
			game.add_dora(int(element.attributes['hai'].value))
			continue
		elif element.nodeName == 'REACH':
			if element.attributes['step'].value == "1":
				# Consume the next element without yielding, so
				# the discard doesn't get shown right without
				# being rotated
				# TODO: this may cause the riichi discard event
				# to get eaten, which breaks the paifu
				riichi = True
				continue
			player = int(element.attributes['who'].value)
			game.riichi(player)
			debug("RIICHI!")
		elif element.nodeName == 'AGARI':
			# Might be worth checking that hai matches the state
			# data
			
			data = {'yaku': element.attributes['yaku'].value,
				'dealer':
				int(element.attributes['fromWho'].value)}
			game.set_event('agari',
					int(element.attributes['who'].value),
					int(element.attributes['machi'].value),
					data)
			# Need to store the data for this somewhere useful
		elif element.nodeName == 'RYUUKYOKU':
			game.set_event('ryuukyoku')
			# identity of the person is in the absence/presence of
			# hai* values
		elif element.nodeName[0] in draw_cmd:
			tile = int(element.nodeName[1:])
			player = draw_cmd.index(element.nodeName[0])
			debug("%s draw %s" % (player, tile_decode(tile)))
			game.draw(player, tile)
		elif element.nodeName[0] in discard_cmd:
			tile = int(element.nodeName[1:])
			player = discard_cmd.index(element.nodeName[0])
			debug("%s discard %s" % (player, tile_decode(tile)))
			game.discard(player, tile)
		elif element.nodeName[0] == 'N':
			player = int(element.attributes['who'].value)
			code = int(element.attributes['m'].value)
			
			call = parse_call(code)
			# Check this for sanity since kans aren't handled
			# properly
			if call:
				game.call(player, call)
			else:
				raise StopIteration # FIXME: Don't pollute the logs for now
			#game.call(player, parse_call(code))

		# Hrm, this may require some adjustment... if a player sets up a
		# riichi and the discard is ronned or called it may not show
		# right
		if not riichi:
			yield game
		else:
			riichi = False
	return

