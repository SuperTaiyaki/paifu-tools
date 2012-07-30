

import sys
from xml.dom.minidom import parse

# Friendlier tile representation
def tile_decode(tile):
	tile /= 4
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

class Player(object):
	def __init__(self):
		self.hand = set() # implicit ordering?
		self.tsumo = None
		self.melds = []
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
		print "Hand before: %s" % (list(self.hand))
		if tile in self.hand:
			self.hand.remove(tile)
			# after a call this could be None
			if self.tsumo:
				self.hand.add(self.tsumo)
		# if not in the hand, it must be the tsumo
		self.tsumo = None
		self.discards.append(tile)
		print "Hand after: %s" % (list(self.hand))

	def riichi(self):
		self.riichitile = self.discards[-1] #len(self.discards)
		# May need to tweak this to account for the tile being called

	# stuff for calls

	def call(self, call):
		for t in call['tiles']:
			self.hand.discard(t)
		#print "Processed call, new hand: "
		#print self.hand
		self.melds.append(call)

	# Mark the last discard as being called by someone else
	def mark_called(self):
		self.called.add(self.discards[-1])

class Game(object):
	def __init__(self):
		self.players = [Player(), Player(), Player(), Player()]

		self.wall = []

		# Basically re-interpreting the log events...
		self.event = ''
		self.tile = -1
		self.player = -1

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
	def call(self, player, tiles):
		self.players[player].call(tiles)
		# The 'dealer' element of the call is relative to the caller,
		# not the client. Push it around a bit.
		dealer = (tiles['dealer'] + player) % 4
		self.players[dealer].mark_called()
		self.event = 'call' # TODO: indicate what the call is
		self.tile = -1 # Uhh...
		self.player = player


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
	print "Dealing with call %d = %x" % (code, code)
	call = {}
	if code & (1 << 2):
		# chi. also matches nuki, but ignoring 3ma
		call['dealer'] = code & 0x3
		tile1 = (code >> 3) & 0x3
		tile2 = (code >> 5) & 0x3
		tile3 = (code >> 7) & 0x3
		base = (code >> 10) & 0x3f
		# actual tile that got called is base % 3
		# NFI what this mess is.
		bn = (((base/3)/7)*9+((base/3)%7))*4

		call['tiles'] = (bn + tile1, bn + 4 + tile2, bn + 8 +
			tile3)
		call['called'] = base % 3

		print "Chi: %s %s %s" % call['tiles']
		return call
	elif code & (0x3c) == 0: # Not complete!
		print "Kan"
		# kan
		tile = code >> 8
		call['called'] = tile % 4
		tile &= ~3 # mask out the called bits
		call['tiles'] = range(tile, tile+4)
		call['dealer'] = code & 0x3
	elif code & 0x1C == 0x8: # 0b111 xx = 0b010 xx
		print "Pon"
		call['dealer'] = code & 0x3
		unused = (code >> 5) & 0x3 # the tile not in the meld
		tiles = code >> 9
		call['called'] = tiles % 3
		base = (tiles / 3) * 4

		call['tiles'] = []
		for i in range (0,4):
			if i == unused:
				continue
			call['tiles'].append(base + i)
	# Should put an exception here
	return call


draw_cmd = ['T', 'U', 'V', 'W'] # self, right, opposite, left
discard_cmd = ['D', 'E', 'F', 'G']
ignore_cmd = ['SHUFFLE', 'GO', 'TAIKYOKU', 'UN', '#text'] # #text is a weird xml thing?

def run_log(stream):
	doc = parse(stream)

	gamelog = doc.firstChild # mjloggm
	game = None
	riichi = False
	for element in gamelog.childNodes:
		#print "Node: " + element.nodeName
		#print "Value: " + str(element.nodeValue)

		if element.nodeName in ignore_cmd:
			continue
		if element.nodeName == 'INIT':
			game = Game()
			hands = []
			for x in range(0,4):
				hand = element.attributes['hai%s' % x].value
				tiles = hand.split(",")
				tiles = [int(x) for x in tiles]
				hands.append(tiles)
			print "HANDS STARTED: %s" % (hands)
			game.deal(hands)
		elif element.nodeName == 'REACH':
			if element.attributes['step'].value == "1":
				# Consume the next element without yielding, so
				# the discard doesn't get shown right without
				# being rotated
				riichi = True
				continue
			player = int(element.attributes['who'].value)
			game.riichi(player)
			print "RIICHI!"
		elif element.nodeName[0] in draw_cmd:
			tile = int(element.nodeName[1:])
			player = draw_cmd.index(element.nodeName[0])
			print "%s draw" % player
			game.draw(player, tile)
		elif element.nodeName[0] in discard_cmd:
			tile = int(element.nodeName[1:])
			player = discard_cmd.index(element.nodeName[0])
			print "%s discard" % player
			game.discard(player, tile)
		elif element.nodeName[0] == 'N':
			player = int(element.attributes['who'].value)
			code =  int(element.attributes['m'].value)
			game.call(player, parse_call(code))

		# Hrm, this may require some adjustment... if a player sets up a
		# riichi and the discard is ronned or called it may not show
		# right
		if not riichi:
			yield game
		else:
			riichi = False
	return

