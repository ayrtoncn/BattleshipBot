import argparse
import json
import os
from random import choice

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
    # print(state)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
        # berisi lokasi kemungkinan dari kapal lawan
    else:
        search_target(state['OpponentMap']['Cells'], map_size)


def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def search_target(opponent_map, map_size):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    targets = []
    print(map_size)
    hit = False
    for cell in opponent_map:
        if cell['Damaged']:
            hit_targets = []
            X = cell['X']
            Y = cell['Y']
            hit = True
            print(X, Y)
            if(Y == 0):
                Ymin = False
            else:
                Ymin = opponent_map[(map_size * X + Y) - 1]['Damaged']
            if(Y == map_size - 1):
                Yplus = False
            else:
                Yplus = opponent_map[(map_size * X + Y) + 1]['Damaged']
            if(X == 0):
                Xmin = False
            else:
                Xmin = opponent_map[(map_size * (X - 1) + Y)]['Damaged']
            if(X == map_size - 1):
                Xmplus = False
            else:
                Xplus = opponent_map[(map_size * (X + 1) + Y)]['Damaged']
            if(not Yplus and not Ymin and not Xplus and not Xmin):
                if(X != map_size - 1 and not opponent_map[(map_size * (X + 1) + Y)]['Missed']):
                    valid_cell = X + 1, Y
                    hit_targets.append(valid_cell)
                if (X != 0 and not opponent_map[(map_size * (X - 1) + Y)]['Missed']):
                    valid_cell = X - 1, Y
                    hit_targets.append(valid_cell)
                if (Y != map_size - 1 and not opponent_map[(map_size * X + Y ) + 1]['Missed']):
                    valid_cell = X, Y + 1
                    hit_targets.append(valid_cell)
                if (Y != 0 and not opponent_map[(map_size * X + Y) - 1]['Missed']):
                    valid_cell = X, Y - 1
                    hit_targets.append(valid_cell)
                print("miss smua")
                targets = hit_targets[:]
                break
            elif(Yplus or Ymin):
                tempY = Y + 1
                while(tempY < map_size and opponent_map[(map_size * X + tempY)]['Damaged']):
                    tempY = tempY + 1
                if(tempY != map_size and not opponent_map[(map_size * X + tempY)]['Missed']):
                    valid_cell = X, tempY
                    hit_targets.append(valid_cell)
                tempY = Y - 1
                while(tempY >= 0 and opponent_map[(map_size * X + tempY)]['Damaged']):
                    tempY = tempY - 1
                if(tempY !=0 and not opponent_map[(map_size * X + tempY)]['Missed']):
                    valid_cell = X, tempY
                    hit_targets.append(valid_cell)
                print("miss Y")
                if(hit_targets != []):
                    targets = hit_targets[:]
                    break
                else:
                    print("hancur")
            elif(Xplus or Xmin):
                tempX = X + 1
                while(tempX < map_size and opponent_map[(map_size * tempX + Y)]['Damaged']):
                    tempX = tempX + 1
                if(tempX != map_size and not opponent_map[(map_size * tempX + Y)]['Missed']):
                    valid_cell = tempX, Y
                    hit_targets.append(valid_cell)
                tempX = X - 1
                while(tempX >= 0 and opponent_map[(map_size * tempX + Y)]['Damaged']):
                    tempX = tempX - 1
                if(tempX !=0 and not opponent_map[(map_size * tempX + Y)]['Missed']):
                    valid_cell = tempX, Y
                    hit_targets.append(valid_cell)
                print("missX")
                if(hit_targets != []):
                    targets = hit_targets[:]
                    break
                else:
                    print("hancur")
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
    target = choice(targets)
    output_shot(*target)
    return


def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    ships = ['Battleship 1 0 north',
             'Carrier 3 1 East',
             'Cruiser 4 2 north',
             'Destroyer 7 3 north',
             'Submarine 1 8 East'
             ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?',
                        help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(
    ), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
