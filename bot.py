import argparse
import json
import os
import math
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
    # print(state['Phase'])
    destroyer = state['OpponentMap']['Ships'][0]['Destroyed'] and state['OpponentMap']['Ships'][2][
        'Destroyed'] and state['OpponentMap']['Ships'][3]['Destroyed'] and state['OpponentMap']['Ships'][4]['Destroyed']
    map_size = state['MapDimension']
    energy = state['PlayerMap']['Owner']['Energy']
    shield_charge = state['PlayerMap']['Owner']['Shield']['CurrentCharges']
    shield_state = state['PlayerMap']['Owner']['Shield']['Active']

    battle_map = initialize_map(map_size)
    if state['Phase'] == 1:
        place_ships()
        save_json((-1,-1,-1),0)
        # berisi lokasi kemungkinan dari kapal lawan
    else:
        with open('data.json', 'r') as outfile:
            data = json.load(outfile)
        score = state['PlayerMap']['Owner']['Points']
        if(score - data['Score'] >= 30):
            destroy = True
            hit = True
        elif (score - data['Score'] == 10):
            destroy = False
            hit = True
        else:
            destroy = False
            hit = False
        lastX = data['PrevCommand'][0][1]
        lastY = data['PrevCommand'][0][2]
        battle_map = update_map(
            state['OpponentMap']['Cells'], battle_map, map_size, destroy, hit, lastX, lastY)
        if (not deploy_shield(state['PlayerMap']['Owner']['Ships'], map_size, shield_charge, shield_state,score)):
            search_target(state['OpponentMap']['Cells'],
                          map_size, destroyer, energy, state['PlayerMap']['Owner']['Ships'], battle_map, destroy, score)


def save_json(prev_command, score):
    data = {}
    data['PrevCommand'] = []
    data['PrevCommand'].append(prev_command)
    data['Score'] = score
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def initialize_map(map_size):
    battle_map = []
    a = (map_size / 2)
    for i in range(map_size):
        temp_battle_map = []
        for j in range(map_size):
            k = i + 1
            l = j + 1
            temp_battle_map.append(
                (-1 * (i - 0) * (i - (map_size - 1))) + (-1 * (j - 0) * (j - (map_size - 1))) + 1)
        battle_map.append(temp_battle_map)
        print(battle_map)
    return battle_map


def update_map(opponent_map, battle_map, map_size, destroy, hit, lastX, lastY):
    if not destroy:
        if not hit:
            for cell in opponent_map:
                X = cell['X']
                Y = cell['Y']
                if not cell['Missed']:
                    battle_map[X][Y] = (-1 * (X - 0) * (X - (map_size - 1))) + (-1 * (Y - 0) * (Y - (map_size - 1))) + 1
                else:
                    battle_map[X][Y] = 0
                if (X == lastX and Y != lastY) and battle_map[X][Y] != 0:
                    if map_size == 7:
                        k = 3
                    elif map_size == 10:
                        k = 5
                    elif map_size == 14:
                        k = 10
                    battle_map[X][Y] -= abs(Y - lastY) * k
                elif (X != lastX and Y == lastY) and battle_map[X][Y] != 0:
                    if map_size == 7:
                        k = 3
                    elif map_size == 10:
                        k = 5
                    elif map_size == 14:
                        k = 10
                    battle_map[X][Y] -= abs(X - lastX) * k
        else:
            for cell in opponent_map:
                X = cell['X']
                Y = cell['Y']
                if (((X == lastX - 1 or X == lastX + 1) and Y == lastY) or (X == lastX and (Y == lastY + 1 or Y == lastY - 1))) and (not cell['Missed'] and not cell['Damaged']):
                    battle_map[X][Y] = 20
                else:
                    battle_map[X][Y] = 0
    else:
        for cell in opponent_map:
            X = cell['X']
            Y = cell['Y']
            if not cell['Missed'] and not cell['Damaged']:
                battle_map[X][Y] = (-1 * (X - 0) * (X - (map_size - 1))) + (-1 * (Y - 0) * (Y - (map_size - 1))) + 1
            else:
                battle_map[X][Y] = 0
    
    print(battle_map)

    '''for ship in ships:
        if(not ship['Destroyed']):
            cell = ship['cell']
            idx = 0
            while(idx <= len(cell)):
                map[cell[idx]['X']][cell[idx]['Y']] = 0
                if((idx != 0 and cell[idx + 1]['X'] == cell[idx]['X']) or (idx != len(cell) and cell[idx + 1]['X'] == cell[idx]['X'])):
                    map[cell[idx]['X'] + 1][cell[idx]['Y']] -= 20
                    map[cell[idx]['X'] - 1][cell[idx]['Y']] -= 20
                    map[cell[idx]['X']][cell[idx]['Y'] + 1] += 20
                    map[cell[idx]['X']][cell[idx]['Y'] + 1] += 20
                elif((idx != 0 and cell[idx + 1]['Y'] == cell[idx]['Y']) or (idx != len(cell) and cell[idx + 1]['Y'] == cell[idx]['Y'])):
                    map[cell[idx]['X'] + 1][cell[idx]['Y']] += 20
                    map[cell[idx]['X'] - 1][cell[idx]['Y']] += 20
                    map[cell[idx]['X']][cell[idx]['Y'] + 1] -= 20
                    map[cell[idx]['X']][cell[idx]['Y'] + 1] -= 20
                idx = idx + 1'''
    return battle_map


def max(battle_map, hit_targets):
    max = hit_targets[0]
    for target in hit_targets:
        if(battle_map[max[0]][max[1]] < battle_map[target[0]][target[1]]):
            max = target
    '''for x in battle_map:
        for y in x:
            if(battle_map[max[0]][max[1]] < battle_map[x][y]):
                max = (x, y)'''
    return max


def find_length(ship_type):
    if (ship_type == 'Submarine'):
        return 3
    elif (ship_type == 'Carrier'):
        return 5
    elif(ship_type == 'Destroyer'):
        return 2
    elif(ship_type == 'Cruiser'):
        return 3
    else:
        return 4


def deploy_shield(ships, map_size, shield_charge, shield_active, score):
    if (map_size == 7):
        return False
    else:
        if ((map_size == 10) and (shield_charge >= 2)) or ((map_size == 14) and (shield_charge >= 3) and not shield_active):
            for ship in ships:
                countBefore = 0
                countHit = 0
                countAfter = 0
                if (not ship['Destroyed']):
                    for cell in ship['Cells']:
                        if (cell['Hit']):
                            countHit = countHit + 1
                            Xhitted = cell['X']
                            Yhitted = cell['Y']
                        elif (countHit == 0):
                            countBefore = countBefore + 1
                        else:
                            countAfter = countAfter + 1
                if (countHit == 0):
                    continue
                else:
                    if (countBefore != 0 and countAfter == 0):
                        Xhitted = ship['Cells'][countBefore]['X']
                        Yhitted = ship['Cells'][countBefore]['Y']
                    deploy_at = Xhitted, Yhitted
                    output_shot(*deploy_at, 8,score)
                    return True
        return False


def output_shot(x, y, move, score):
    # move = 1  # 1=fire shot command code
    save_json((move, x, y), score)
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def search_target(opponent_map, map_size, destroyer, energy, ship, battle_map, destroy, score):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)
    targets = []
    temp_targets = []
    hit_targets = []
    DoubleVertikal = ship[1]['Weapons'][1]['EnergyRequired']
    DoubleHorizontal = ship[1]['Weapons'][1]['EnergyRequired']
    Corner = ship[3]['Weapons'][1]['EnergyRequired']
    CrossDiagonal = ship[2]['Weapons'][1]['EnergyRequired']
    CrossHorizontal = ship[4]['Weapons'][1]['EnergyRequired']
    Seeker = ship[0]['Weapons'][1]['EnergyRequired']

    if(destroyer):
        # tinggal kapal yang panjangnya 2 tembak dengan jarak selang 2
        shot = 2
    else:
        shot = 3

    for cell in opponent_map:
        if cell['Damaged'] and not destroy:
            # hit_targets adalah target yang mungkin ditembak
            X = cell['X']
            Y = cell['Y']
            # cek kiri kanan atas bawah kalau yang atas udh kena maka tembaknya ke atas kalau ga kebawahnya dan sebaliknya
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
                Xplus = False
            else:
                Xplus = opponent_map[(map_size * (X + 1) + Y)]['Damaged']
            if(not Yplus and not Ymin and not Xplus and not Xmin):
                # target baru ditemukan belum sekeliling target masih belum tertembak
                if(X != map_size - 1 and not opponent_map[(map_size * (X + 1) + Y)]['Missed']):
                    # cek X+1 kalau msh belum ditembak masukan X+1 ke hit_targets
                    valid_cell = X + 1, Y
                    hit_targets.append(valid_cell)
                if (X != 0 and not opponent_map[(map_size * (X - 1) + Y)]['Missed']):
                    # cek X-1 kalau msh belum ditembak masukan X-1 ke hit_targets
                    valid_cell = X - 1, Y
                    hit_targets.append(valid_cell)
                if (Y != map_size - 1 and not opponent_map[(map_size * X + Y) + 1]['Missed']):
                    # cek Y+1 kalau msh belum ditembak masukan Y+1 ke hit_targets
                    valid_cell = X, Y + 1
                    hit_targets.append(valid_cell)
                if (Y != 0 and not opponent_map[(map_size * X + Y) - 1]['Missed']):
                    # cek Y-1 kalau msh belum ditembak masukan Y-1 ke hit_targets
                    valid_cell = X, Y - 1
                    hit_targets.append(valid_cell)
                # prioritaskan menembak target yang disekitar titik yang sudah tertembak dulu
                targets = hit_targets[:]
                break
            elif(Yplus or Ymin):
                # target sudah memiliki hit di atasnya atau dibawahnya
                tempY = Y + 1
                while(tempY < map_size and opponent_map[(map_size * X + tempY)]['Damaged']):
                    # telusuri terus keatas hingga menemukan titik yang damaged
                    tempY = tempY + 1
                if(tempY != map_size and not opponent_map[(map_size * X + tempY)]['Missed']):
                    # bila titik belum ditembak maka tembak
                    valid_cell = X, tempY
                    hit_targets.append(valid_cell)
                tempY = Y - 1
                while(tempY >= 0 and opponent_map[(map_size * X + tempY)]['Damaged']):
                    # telusuri terus kebawah hingga menemukan titik yang belum damaged
                    tempY = tempY - 1
                if(tempY >= 0 and not opponent_map[(map_size * X + tempY)]['Missed']):
                    # bila titik belum ditembak maka tembak
                    valid_cell = X, tempY
                    hit_targets.append(valid_cell)
                if(hit_targets != []):
                    # prioritaskan menembak target yang disekitar titik yang sudah tertembak dulu
                    targets = hit_targets[:]
                    break
            elif(Xplus or Xmin):
                # target sudah memiliki hit di kiri atau di kanannya
                tempX = X + 1
                while(tempX < map_size and opponent_map[(map_size * tempX + Y)]['Damaged']):
                    # telusuri ke terus kekanan hingga ditemukan titik yang belum damaged
                    tempX = tempX + 1
                if(tempX != map_size and not opponent_map[(map_size * tempX + Y)]['Missed']):
                    # jika titik belum tertembak maka tembak
                    valid_cell = tempX, Y
                    hit_targets.append(valid_cell)
                tempX = X - 1
                while(tempX >= 0 and opponent_map[(map_size * tempX + Y)]['Damaged']):
                    # telusuri terus kekiri hingga ditemukan titik yang belum damaged
                    tempX = tempX - 1
                if(tempX >= 0 and not opponent_map[(map_size * tempX + Y)]['Missed']):
                    # bila titik belum tertembak maka tembak
                    valid_cell = tempX, Y
                    hit_targets.append(valid_cell)
                if(hit_targets != []):
                    # prioritaskan menembak target yang disekitar titik yang sudah tertembak dulu
                    targets = hit_targets[:]
                    break
        if not cell['Damaged'] and not cell['Missed']:
            # jika cell belum damaged maupun masih missed
            # xmin,ymin, xplus, y plus berguna untuk mengecek sekeliling target dan minmin dan plusplus mengecek 2 kotak dari target
            X = cell['X']
            Y = cell['Y']
            if(Y == 0):
                Ymin = False
                Yminmin = False
            else:
                Ymin = opponent_map[(
                    map_size * X + Y) - 1]['Missed'] or opponent_map[(map_size * X + Y) - 1]['Damaged']
                if(shot == 3):
                    if(Y != 1):
                        Yminmin = opponent_map[(
                            map_size * X + Y) - 2]['Missed'] or opponent_map[(map_size * X + Y) - 2]['Damaged']
                    else:
                        Yminmin = False
                else:
                    Yminmin = False
            if(Y == map_size - 1):
                Yplus = False
                Yplusplus = False
            else:
                Yplus = opponent_map[(
                    map_size * X + Y) + 1]['Missed'] or opponent_map[(map_size * X + Y) + 1]['Damaged']
                if(shot == 3):
                    if(Y != map_size - 2):
                        Yplusplus = opponent_map[(
                            map_size * X + Y) + 2]['Missed'] or opponent_map[(map_size * X + Y) + 2]['Damaged']
                    else:
                        Yplusplus = False
                else:
                    Yplusplus = False
            if(X == 0):
                Xmin = False
                Xminmin = False

            else:
                Xmin = opponent_map[(
                    map_size * (X - 1) + Y)]['Missed'] or opponent_map[(map_size * (X - 1) + Y)]['Damaged']
                if(shot == 3):
                    if(X != 1):
                        Xminmin = opponent_map[(
                            map_size * (X - 2) + Y)]['Missed'] or opponent_map[(map_size * (X - 2) + Y)]['Damaged']
                    else:
                        Xminmin = False
                else:
                    Xminmin = False
            if(X == map_size - 1):
                Xplus = False
                Xplusplus = False
            else:
                Xplus = opponent_map[(
                    map_size * (X + 1) + Y)]['Missed'] or opponent_map[(map_size * (X + 1) + Y)]['Damaged']
                if(shot == 3):
                    if(X != map_size - 2):
                        Xplusplus = opponent_map[(
                            map_size * (X + 2) + Y)]['Missed'] or opponent_map[(map_size * (X + 2) + Y)]['Damaged']
                    else:
                        Xplusplus = False
                else:
                    Xplusplus = False
            if not(((Ymin and Yplus) or (Xmin and Xplus)) or ((Yminmin and Yplusplus) or (Xminmin and Xplusplus))):
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            valid_cell = cell['X'], cell['Y']
            temp_targets.append(valid_cell)
            # temp target berguna untuk menembak target secara random jika kondisi tidak ada yang memenuhi
    if(targets == []):
        # jika target tidak ada yang memenuhi tembak random
        targets = temp_targets[:]
    if(hit_targets != targets):
        if(energy >= Seeker and not ship[0]['Destroyed']):
            move=7
        elif(ship[0]['Destroyed'] and energy >= CrossDiagonal and not ship[2]['Destroyed']):
            move=5
        elif(ship[0]['Destroyed'] and ship[2]['Destroyed'] and energy >= CrossHorizontal and not ship[4]['Destroyed']):
            move=6
        elif(ship[0]['Destroyed'] and ship[2]['Destroyed'] and ship[4]['Destroyed'] and energy >= Corner and not ship[3]['Destroyed']):
            move=4
        elif(ship[0]['Destroyed'] and ship[2]['Destroyed'] and ship[4]['Destroyed'] and ship[3]['Destroyed'] and energy >= DoubleVertikal and not ship[1]['Destroyed']):
            move=choice([1, 2])
        else:
            move = 1
    else:
        move = 1
        # prioritaskan seeker missile karena seeker akan menembak target yang berada pada jarak 5X5 dari titik tengah yang kita tuju. jadi akan lebih membantu saat digunakan
    #target = choice(targets)
    target = max(battle_map, targets)
    output_shot(*target, move, score)
    return


def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    pilihan = choice([1, 2])
    if (map_size == 7):
        if (pilihan == 1):
            ships = ['Battleship 3 3 East',
                     'Carrier 0 1 north',
                     'Cruiser 2 1 north',
                     'Destroyer 5 0 East',
                     'Submarine 4 5 East'
                     ]
        else:
            ships = ['Battleship 0 2 north',
                     'Carrier 2 3 East',
                     'Cruiser 4 0 north',
                     'Destroyer 0 0 East',
                     'Submarine 4 6 East'
                     ]

    elif(map_size == 10):
        if (pilihan == 1):
            ships = ['Battleship 1 0 north',
                     'Carrier 3 1 East',
                     'Cruiser 5 7 north',
                     'Destroyer 7 3 north',
                     'Submarine 1 8 East'
                     ]
        else:
            ships = ['Battleship 3 0 East',
                     'Carrier 1 2 north',
                     'Cruiser 3 7 East',
                     'Destroyer 8 3 East',
                     'Submarine 9 7 north'
                     ]

    else:
        if (pilihan == 1):
            ships = ['Battleship 0 9 East',
                     'Carrier 9 11 East',
                     'Cruiser 10 3 north',
                     'Destroyer 12 2 East',
                     'Submarine 2 1 north'
                     ]
        else:
            ships = ['Battleship 6 11 East',
                     'Carrier 1 5 north',
                     'Cruiser 12 7 north',
                     'Destroyer 0 1 East',
                     'Submarine 13 0 north'
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
