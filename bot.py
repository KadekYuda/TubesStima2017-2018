import argparse
import json
import os
from random import choice
from pathlib import Path

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0


def main(player_key):
    global map_size
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        if os.path.isfile('target.txt'):
            os.remove('target.txt')
        place_ships()
    else:
        fire_shot(state['OpponentMap']['Cells'])


def output_shot(move, x, y):
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    if not os.path.exists("targets.txt"):
        # File not found
        not_shot_yet = available_square(opponent_map)
        move = 1
        target = choice(not_shot_yet)
        targets = [target]
        with open('targets.txt', 'w') as fp:
            fp.write('\n'.join('%d %d' % x for x in targets))
        fp.close()
        output_shot(move, *target)
        return
    else:
        # File found
        targets = [] # list yang menyimpan target yang akan ditembak berikutnya
        with open('targets.txt', 'r') as fo:
            for i in fo.readlines():
                tmp = i.split(" ")
                try:
                    targets.append((int(tmp[0]), int(tmp[1])))
                except:
                    pass
        last_shot = targets.pop()
        # access map: last_shot[1]+last_shot[0]*map_size]
        if opponent_map[last_shot[1] + (last_shot[0] * map_size)]['Damaged']:
            # append 4 more targets
            # x+1 , y
            if last_shot[0]+1 < map_size and not (opponent_map[last_shot[1] + (last_shot[0]+1)*map_size]['Damaged']) and not (opponent_map[last_shot[1] + (last_shot[0]+1)*map_size]['Missed']):
                targets.append((last_shot[0] + 1, last_shot[1]))
            # x-1, y
            if last_shot[0]-1 >= 0 and not (opponent_map[last_shot[1] + (last_shot[0]-1)*map_size]['Damaged']) and not (opponent_map[last_shot[1] + (last_shot[0]-1)*map_size]['Missed']):
                targets.append((last_shot[0] - 1, last_shot[1]))
            # x, y+1
            if last_shot[1]+1 < map_size and not (opponent_map[last_shot[1]+1 + (last_shot[0])*map_size]['Damaged']) and not (opponent_map[last_shot[1]+1 + (last_shot[0])*map_size]['Missed']):
                targets.append((last_shot[0], last_shot[1] + 1))
            # x, y-1
            if last_shot[1]-1 >= 0 and not (opponent_map[last_shot[1]-1 + (last_shot[0])*map_size]['Damaged']) and not (opponent_map[last_shot[1]-1 + (last_shot[0])*map_size]['Missed']):
                targets.append((last_shot[0], last_shot[1] - 1))
            move = 1
            if len(targets) == 0:
                not_shot_yet = available_square(opponent_map)
                move = 1
                target = choice(not_shot_yet)
                targets.append(target)
                with open('targets.txt', 'w') as fp:
                    fp.write('\n'.join('%d %d' % x for x in targets))
                fp.close()
                output_shot(move, *target)
                return
            else:
                target = targets[-1]
                with open('targets.txt', 'w') as fp:
                    fp.write('\n'.join('%d %d' % x for x in targets))
                fp.close()
                output_shot(move, *target)
                return
        else:
            if opponent_map[last_shot[1] + (last_shot[0] * map_size)]['ShieldHit']:
                targets.insert(0, (last_shot[0],last_shot[1]))
            if len(targets) == 0 or (opponent_map[last_shot[1] + (last_shot[0] * map_size)]['ShieldHit'] and len(targets) == 1):
                not_shot_yet = available_square(opponent_map)
                move = 1
                target = choice(not_shot_yet)
                targets.append(target)
                with open('targets.txt', 'w') as fp:
                    fp.write('\n'.join('%d %d' % x for x in targets))
                fp.close()
                output_shot(move, *target)
                return
            else:
                # use top as new target
                move = 1
                target = targets[-1]
                with open('targets.txt', 'w') as fp:
                    fp.write('\n'.join('%d %d' % x for x in targets))
                fp.close()
                output_shot(move, *target)
                return


def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west
    # x = 0 di kiri
    # y = 0 di bawah
    # north ke atas, south ke bawah
    # west ke kiri, east ke kanan
    if map_size == 10:
        ships = ['Battleship 1 0 north',
                 'Carrier 3 1 East',
                 'Cruiser 4 2 north',
                 'Destroyer 7 3 north',
                 'Submarine 1 8 East'
                 ]
    elif map_size == 7:
        ships = ['Battleship 1 2 north',
                 'Carrier 0 0 East',
                 'Cruiser 6 2 north',
                 'Destroyer 4 5 north',
                 'Submarine 3 3 East'
                 ]
    elif map_size == 14:
        ships = ['Battleship 2 7 north',
                 'Carrier 4 12 East',
                 'Cruiser 10 2 north',
                 'Destroyer 2 0 north',
                 'Submarine 11 10 East'
                 ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return


def available_square(opponent_map):
    not_shot_yet = []
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed'] and (int(cell['X']) + int(cell['Y']) % 2 != 0):
            valid_cell = cell['X'], cell['Y']
            not_shot_yet.append(valid_cell)
    if len(not_shot_yet) == 0:
        for cell in opponent_map:
            if not cell['Damaged'] and not cell['Missed']:
                valid_cell = cell['X'], cell['Y']
                not_shot_yet.append(valid_cell)
    return not_shot_yet


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
