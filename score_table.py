#!/usr/bin/python2

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

	return (tsumo, ko, oya, "%s_%s" % (han, "o" if dealer else "k"))

table = [[4, 3, 2, 1, '', 1, 2, 3, 4]]
for fu in xrange(20, 80, 10):
	row = [score(fu, x, True) for x in range(4, 0, -1)]
	row.append(fu)
	row.extend([score(fu, x, False) for x in range(1, 5)])
	table.append((fu, row))

def display(col):

	if isinstance(col, int):
		return "<td><h2>%s</h2></td>" % col
	# dealer ron-only corner
	# ko only-only corner
	# Mangan cases
	# Everything else
	
	if col[2] != -1:
		rest = "%d/%d" % (col[2], col[1])
	else:
		rest = "%d" % col[1]

	return '<td class="%s_han"><b>%d</b><br />%s</td>' % (col[3], col[0], rest)

# Header row
print "<table>\n<tr>"
for col in table[0]:
	print "<th>%s</th>" % col
print "</tr>\n<tr>"

# 20fu row - no tsumo
#for col in table[1]:
#	print "<td>%s</td>" % str(col)
#print "</tr>" # Opened at the close of the thead above

for row in table[1:]:
	print '<tr class="%s_fu">' % row[0]
	for col in row[1]:
		#print "<td>",
		# print col
		print display(col)
		#print col,
		#print "</td>"
	print "</tr>"

print "</table>"
