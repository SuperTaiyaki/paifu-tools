#!/usr/bin/python 
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import tenhou
import sys
import json

game = tenhou.run_log(sys.stdin)

for state in game:
    if state.event == 'agari':
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
            discards.append(player.discards)
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

        waits = tenhou.agari_tiles([x/4 for x in hands[winner]])
        print json.dumps({'hands': hands, 'discards': discards, 'melds': melds,
            'riichi': riichi, 'waits': waits})
