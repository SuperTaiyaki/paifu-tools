#!/usr/bin/python 
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import tenhou
import sys
import json
import time

# STORAGE FORMAT
# hands: [[tile]*1-13]*4 (tile 1-135)
# discards: [[tile | flags]*0-18] * 4 (tile 0-135)
# flags are tenhou.DISCARD_* * 1024, tile is tile % 1024, 1024 allows for
# shifting and masking
# melds: tenhou meld format {'tiles', 'type', 'dealer'} first of 'tiles' is the
# called tile
# waits: [tile]*1-13? (tile 0-34)
# player: player who goes out (usual tenhou ordering, 1-3)
# dealer: east wind (0-3)
# round: current round number (0-12, 0-3 is east, 4-7 is south...)
# dora: list of dora (indicators? not yet confirmed)

id = int(time.time() * 1000)

game = tenhou.run_log(sys.stdin)
for state in game:
    if state.event == 'agari':
        # state.data is the event data (i.e. the deal-in), state.dealer is the
        # east player
        if state.data['dealer'] == state.player:
            continue # tsumo, don't record

        # Players need to be rearranged so that 0 is the one who dealt
        # in
        player_order = [(x + state.data['dealer']) % 4 for x in range(4)]
        order_inverse = [(x - state.data['dealer']) % 4 for x in range(4)]
        winner = order_inverse[state.player]
        hands = []
        discards = []
        melds = []
        riichi = []

        for p in player_order:
            player = state.players[p]
            hands.append(sorted(list(player.hand)))
            # Filter the discards. Pack the flags into the tile number
            discards.append([tile + (flag * 1024) for tile, flag in player.discards])
            p_melds = []
            for meld in player.melds:
                p_melds.append({'tiles': meld['tiles'],
                    'type': meld['type'],
                    'dealer': order_inverse[meld['dealer']]})
            melds.append(p_melds) #need to remap some numbers in here

            if player.riichitile in player.discards:
                riichi.append(player.discards.index(player.riichitile))
            else:
                riichi.append(-1)

        # This state is captured just after the player dealt in - load the tile
        # back into the hand
        player = order_inverse[state.data['dealer']]
        tile = discards[player].pop() % 1024
        hands[player].append(tile)
        hands[player].sort() # Don't let the hot tile sit at the end!

        waits = tenhou.agari_tiles([x/4 for x in hands[winner]])

        f = open("hand%08d" % id, "w")
        json.dump({'hands': hands,
            'discards': discards,
            'melds': melds,
            'riichi': riichi,
            'waits': waits,
            'player': order_inverse[state.player],
            'dealer': order_inverse[state.dealer],
            'round': state.round, 
            'dora': state.dora}, f)
        f.close()
        id += 1
