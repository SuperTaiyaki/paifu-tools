#!/usr/bin/python2

import tenhou
import unittest
# Build this into a proper unit test framework sometime

def show_call(call):
	result = tenhou.parse_call(call)
	print "Caller: %s" % result['dealer']
	print "Tiles: %s" % tenhou.convert_tiles(result['tiles'])

# from tenhoudoc.txt
# sample: 0011110100110111
show_call(0b0011110100110111)
# should be (3, [22, 25, 30])

# From annotated log
# north (right player) chi 4m from west ([4m]23m)
show_call(5391)
# west (right) pon west from south
show_call(44555)
# south (self) pon north from north
show_call(46122)
# west chi 3p from south ([3]12p)
show_call(23735)
# west (right) chi 2s from south ([2]34s)
show_call(46399)
# east (left) chi 3m from north ([3]24m)
show_call(4391)
# west pon west from east
show_call(45642)

# ankan 8p
show_call(16896)

# Unknown calls, taken from mygame.log
#for call in [46335, 29935, 26633, 45577, 57423]:
#	print tenhou.parse_call(call)

print '--------------------------------------------'
def show_hand(tiles):
	print [tenhou.tile_decode(tile*4) for tile in tiles]

show_hand(tenhou.reduce([29]*4 + [30]*3))
show_hand(tenhou.reduce([2,3,4,5]))
show_hand(tenhou.reduce([7,8,9,10]))
show_hand(tenhou.reduce([2,3,4,3,3,4,5]))

