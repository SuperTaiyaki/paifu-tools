#!/usr/bin/python

import math

def score(fu, han, dealer = False):
	base = fu * 2**(2 + han) / 100.0
	if base > 20:
		base = 20 # mangan

	if dealer:
		base *= 2
		tsumo = math.ceil(3*base) * 100
		oya = -1
	else:
		tsumo = math.ceil(4*base) * 100
		oya = math.ceil(base*2) * 100
	ko = math.ceil(base) * 100

	return (tsumo, ko, oya)

table = [[4, 3, 2, 1, '', 1, 2, 3, 4]]
for fu in xrange(20, 80, 10):
	row = [score(fu, x, True) for x in range(4, 0, -1)]
	row.append(fu)
	row.extend([score(fu, x, False) for x in range(1, 5)])
	table.append(row)

def display(col):
	# dealer ron-only corner
	# ko only-only corner
	# Mangan cases
	# Everything else
	pass

# Header row
print "<table>\n<tr>"
for col in table[0]:
	print "<th>%s</th>" % col,
print "</tr>\n<tr>"

# 20fu row - no tsumo
for col in table[1]:
	print "<td>%s</td>" % col
print "</tr>" # Opened at the close of the thead above

for row in table[1:]:
	print "<tr>"
	for col in row:
		print "<td>",
		print col,
		print "</td>"
	print "</tr>"

