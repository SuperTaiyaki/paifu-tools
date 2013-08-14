import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle, BindTexture, Scale, Rotate, Translate, PushMatrix, PopMatrix
from tenhou import *
#from kivy.graphics.context_instructions import Scale, Rotate, Translate, PushMatrix, PopMatrix

# Basic replay viewer, basically just verification of the main tenhou code.

tilelist = []
for x in range(0, 9):
#        tilelist.append(Image(source="%sm.gif" % (x+1)))
        tilelist.append("images/%sm.png" % (x+1))
for x in range(0, 9):
#        tilelist.append(Image(source="%sp.gif" % (x+1)))
        tilelist.append("images/%sp.png" % (x+1))
for x in range(0, 9):
#        tilelist.append(Image(source="%ss.gif" % (x+1)))
        tilelist.append("images/%ss.png" % (x+1))
for x in range(0, 8):
#        tilelist.append(Image(source="%sz.gif" % (x+1)))
        tilelist.append("images/%sz.png" % (x+1))

def draw_tile(tile, rotated = False):
	if rotated:
		Rotate(90, 0, 0, 1)
		# no idea why pos isn't 80 or 120
		Rectangle(pos=(0,-100), size=(80, 95),
				source=tilelist[tile / 4])
		Rotate(-90, 0, 0, 1)
		Translate(120, 0, 0)
	else:
		Rectangle(pos=(0,0), size=(80, 95),
			source=tilelist[tile / 4])
		Translate(80, 0, 0)

def draw_call(call):
	# first element of the array is the called tile
        # TODO: this is putting the rotated tile in the entirely wrong place
	idx = 0 # Yes, backwards
	for tile in call['tiles']:
		# Will require some adjustment for kans, since dealer=right gets
		# placed on the edge, not the 3rd tile
		if idx == call['dealer']:
			# Draw sideways
			draw_tile(tile, True)
		else:
			draw_tile(tile)
		idx += 1
	Color(1,1,1)

def draw_player(canvas, player, position):
	hand = list(player.hand)
	hand.sort()
	#print "About to redraw hand: %s" % (hand)
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
			draw_tile(tile)

		if player.tsumo:
			PushMatrix()
			Translate(-120, 100, 0)
			draw_tile(player.tsumo, True)
			PopMatrix()

		# Should really be called calls
		# Should also be anchored to the right so it doesn't move with
		# the hand
		for meld in player.melds:
			Translate(150, 0, 0)
			draw_call(meld)
			print meld

		PopMatrix()
		col_start = -400
		Translate(-400, -400, 0)
		i = 0
		for (tile, flags) in player.discards:
			if flags & DISCARD_CALLED:
				Color(0.5, 0.5, 0.5)
			else:
				Color(1, 1, 1)
			rotated = (flags & DISCARD_RIICHI)
			# TODO: tsumokiri flag
			draw_tile(tile, rotated)
			i += 1
			if i == 6:
				i = 0
				Translate(-480, -120, 0)

		# TODO: riichi stick

		PopMatrix()
	#print "Done drawing."


class Table(Widget):
	def __init__(self, **kwargs):

		super(Table, self).__init__(**kwargs)

		with self.canvas:
			Color(0.24,0.47,0.25)
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

		# If there's a call to notify, draw it on the screen too
		#if game.event == 'riichi':


class TenhouViewer(App):
	def build(self):
		return Table() 

if __name__ == '__main__':
	app = TenhouViewer()
	app.run()

