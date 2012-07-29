import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import RenderContext, Color, Rectangle, BindTexture, Scale, Rotate, Translate, PushMatrix, PopMatrix
from tenhou import *
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
			PushMatrix()
			Translate(-20, 110, 0)
			Rotate(90, 0, 0, 1)
			Rectangle(pos=(0, 0), size=(80, 120),
				source=tilelist[player.tsumo / 4])
			PopMatrix()

		for meld in player.melds:
			Translate(30, 0, 0)
			print meld
			for tile in meld:
				Translate(80, 0, 0)
				Rectangle(pos=(0,0), size=(80, 120),
						source=tilelist[tile / 4])

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

