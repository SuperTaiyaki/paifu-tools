

import sys
from xml.dom.minidom import parse
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle, BindTexture, Scale, Rotate, Translate, PushMatrix, PopMatrix
#from kivy.graphics.context_instructions import Scale, Rotate, Translate, PushMatrix, PopMatrix

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

class Player(object):
	def __init__(self):
		self.hand = set() # implicit ordering?
		self.tsumo = None
		self.melds = []
		self.discards = [] # ordered
		self.reachtile = None
	
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

	def reach(self):
		self.reachtile = len(self.discards)
	
	# stuff for calls

	def call(self, tiles):
		for t in tiles:
			self.hand.discard(t)
		print "Processed call, new hand: "
		print self.hand
		self.melds.append(tiles)

def draw_player(canvas, player, position):
	print player.hand
	hand = list(player.hand)
	hand.sort()
	print hand
	print "About to redraw hand: %s" % (hand)
	with canvas:
		Color(0, 0.7, 0)
		#Rectangle(size=(1024,1024))
		Color(1,1,1)

		# Not GL, not 2D... thoroughly fucked up. I don't think I like
		# Kivy.
		PushMatrix()
		# Would be nice to somehow center this so that only rotation has
		# to change for each player
		#Translate(800, 0, 0)

		Scale(0.35)
		# nfi where this number comes from, just making it work
		Translate(1200, 900, 0)
		# For re-centering matrices
		Rectangle(pos=(-10, -10), size=(20, 20))

		Rotate(90*position, 0, 0, 1)

		PushMatrix()
		Translate(-600, -780, 0)
		for tile in hand:
			Translate(80, 0, 0)
			Rectangle(pos=(0,0), size=(80, 120),
					source=tilelist[tile / 4])
		if player.tsumo:
			Translate(-20, 110, 0)
			Rotate(90, 0, 0, 1)
			Rectangle(pos=(0, 0), size=(80, 120),
				source=tilelist[player.tsumo / 4])
		PopMatrix()
		col_start = -400
		Translate(-400, -400, 0)
		i = 0
		for tile in player.discards:
			# TODO: rotated tile for riichi
			# TODO: something about called tiles
			Rectangle(pos=(0, 0), size=(80, 120),
				source=tilelist[tile / 4])
			Translate(80, 0, 0)
			i += 1
			if i == 6:
				i = 0
				Translate(-480, -120, 0)

		# TODO: riichi stick

		PopMatrix()
	print "Done drawing."

class Game(object):
	def __init__(self):
		self.players = [Player(), Player(), Player(), Player()]

		self.wall = []

	# wall generation NYI, too complicated
	
	def deal(self, players):
		for i in range(0,4):
			self.players[i].draw(players[i])

	def draw(self, player, tile):
		self.players[player].draw1(tile)
	def discard(self, player, tile):
		self.players[player].discard(tile)

	def reach(self, player):
		self.players[player].reach()

	def call(self, player, tiles):
		self.players[player].call(tiles)


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
	if code & (1 << 2):
		# chi. also matches nuki, but ignoring 3ma
		dealer = code & 0xf
		tile1 = (code >> 4) & 0xf
		tile2 = (code >> 6) & 0xf
		tile3 = (code >> 8) & 0xf
		base = (code >> 11) & 0x3f
		# actual tile that got called is base % 3

		print "Chi: %s %s %s" % (base + tile1, base + 4 + tile2, base + 8 +
			tile3)

		# Have to mangle base or something?
		return (dealer, [base + tile1, base + 4 + tile2, base + 8 +
			tile3])
	elif code & (0x3c) == 0: # ignoring this "extended kan" thing....
		print "Kan"
		# kan
		tile = code >> 8
		dealer = code & 0xf
		return (dealer, range(tile, tile+4))
	elif code & 0x1C == 0x8:
		print "Pon"
		dealer = code & 0xf
		unused = (code >> 5) & 0xf
		tiles = ((code >> 9) / 3) * 4
		# The actual tile that got called is (code >>9) % 3 (index into
		# called, probably)
		called = []
		for i in range (0,4):
			if i == unused:
				continue
			called.append(tiles + i)
		return (dealer, called)

	return (0, [])


draw_cmd = ['T', 'U', 'V', 'W'] # self, right, opposite, left
discard_cmd = ['D', 'E', 'F', 'G']
ignore_cmd = ['SHUFFLE', 'GO', 'TAIKYOKU', 'UN', '#text'] # #text is a weird xml thing?

def run_log(stream):
	doc = parse(stream)

	gamelog = doc.firstChild # mjloggm
	game = None
	for element in gamelog.childNodes:
		print "Node: " + element.nodeName
		print "Value: " + str(element.nodeValue)

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
			if element.attributes['step'].value == "2":
				continue # step 2, don't care
			player = int(element.attributes['who'].value)
			game.reach(player)
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
			(dealer, tiles) = parse_call(code)
			game.call(player, tiles)

		print "Yielding!"
		yield game
	return

class Table(Widget):
	def __init__(self, **kwargs):

		super(Table, self).__init__(**kwargs)

		with self.canvas:
			Color(0.24,0.47,0.25)
			BindTexture(source='tile.png', index=1)
			Rectangle(size=(1024,1024))
		self.game_iter = run_log(sys.stdin)
		self.game_iter.next()

	def on_touch_down(self, touch):
		with self.canvas:
			Color(0.24,0.47,0.25)
			Rectangle(size=(1024,1024))
		game = self.game_iter.next()
		draw_player(self.canvas, game.players[0], 0)
		draw_player(self.canvas, game.players[1], 1)
		draw_player(self.canvas, game.players[2], 2)
		draw_player(self.canvas, game.players[3], 3)

class TenhouViewer(App):
	def build(self):
		return Table() 

if __name__ == '__main__':
	app = TenhouViewer()
	app.run()

