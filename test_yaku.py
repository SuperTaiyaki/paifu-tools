#!/usr/bin/python2
import unittest
import tenhou

# Testing the agari-related functions of tenhou.py
"""
Completion status:
# 1 han
0: 'tsumo',
1: 'riichi',
2: 'ippatsu',
3: 'chankan',
4: 'rinshan kaihou',

5: 'haitei', # check
6: 'houtei', # check
7: 'pinfu', 
*8: 'tanyao',
+9: 'iipeikou',

10: 'ton', # jikaze
11: 'nan',
12: 'xia',
13: 'pei',

14: 'ton', # bakaze
15: 'nan',
16: 'xia', #rare!
17: 'pei', # super rare

18: 'haku',
19: 'hatsu',
20: 'chun',

# 2 han
21: 'double riichi',
22: 'chiitoitsu',
23: 'chanta', #open, unconfirmed (chis not visible)
+24: 'ikkitsuukan', #open
+25: 'sanshokudoujun', # open?

+26: 'sanshokudoukou',
27: 'sankantsuu',
28: 'toitoihou',
29: 'sanankou',
30: 'shousangen',
31: 'honroutou',

# 3 han
32: 'ryanpeikou',
33: 'chanta', # closed
34: 'honitsu', # closed

# 6 han
+35: 'chinitsu', # open

# yakuman sit in here

52: 'dora',
53: 'uradora',
54: 'red5'
"""

# TODO: Make this work off log data too!
# Or generate off log data
class TenhouYakuTest(unittest.TestCase):
	def hand_yaku(self, tiles, yaku):
		hand = tenhou.read_tiles(tiles)
		parts = tenhou.agari_structures(hand)
		for structure in parts:
			print(structure)
			yaku_list = tenhou._count_score([], structure, 0, 0, 0, hand[0])
			for y in yaku_list:
				print y
				if yaku == y[0]:
					return True
		return False

		
	def test_pinfu(self):
		# "123789m34p34599s" draw/ron 5p
		# Check fail on 
		# "123789m35p34599s" draw/ron 4p (kanchan)
		# penchan
		# winds
		pass

	def test_tanyao(self):
		# "23423423423455p" 
		self.assertEqual(self.hand_yaku("23423423423455p", 'tanyao'), True)
		self.assertEqual(self.hand_yaku("234234234234p11s", 'tanyao'), False)

	def test_ikki(self):
		self.assertEqual(self.hand_yaku("123456789m45699s", 'ittsuu'), True)
	
	def test_sanshoku(self):
		self.assertEqual(self.hand_yaku("234m234789s23455p", 'sanshoku'), True)
	def test_sanshokudoujun(self):
		self.assertEqual(self.hand_yaku("444m444789p44411s", 'sanshokudoujun'), True)

	def test_iipeikou(self):
		self.assertEqual(self.hand_yaku("234234m333444s88p", 'iipeikou'), True)

	def test_chinitsu(self):
		self.assertEqual(self.hand_yaku("11223345656799s", 'chinitsu'), True)

if __name__ == '__main__':
	#if not hand_yaku("23423423423455p", 'tanyao'):
	unittest.main()

