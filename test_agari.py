#!/usr/bin/env python
import unittest
import tenhou

# Testing the agari-related functions of tenhou.py

class TenhouAgariTest(unittest.TestCase):
	def test_pair(self):
		self.assertEqual(tenhou.agari([1,1]), True)
	def test_nobetan(self):
		hand = [1,2,3,4]
		# Check that the [1,2,3] doesn't break the pair
		self.assertEqual(tenhou.agari(hand + [1]), True)
		self.assertEqual(tenhou.agari(hand + [4]), True)
	def test_iipeikou(self):
		# Check that the pair isn't taken too early
		self.assertEqual(tenhou.agari([1,2,3,1,2,3,7,7]), True)
	def test_koutsu(self):
		# Check that the [3,3,3] doesn't get taken incorrectly (breaks the runs)
		self.assertEqual(tenhou.agari([1,2,3,2,3,4,3,4,5,7,7]), True)
	
	def test_chiitoitsu(self):
		self.assertEqual(tenhou.chiitoitsu([1,1,2,2,3,3,4,4,5,5,6,6,7,7]), True)
		self.assertEqual(tenhou.chiitoitsu([1,1,2,2,3,3,4,4,5,5,6,6,7,8]), False)

if __name__ == '__main__':
	unittest.main()

