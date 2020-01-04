from rubik import cube

X_ROT_CW = {
    'U': 'F',
    'B': 'U',
    'D': 'B',
    'F': 'D',
    'E': 'Si',
    'S': 'E',
    'Y': 'Z',
    'Z': 'Yi',
}
Y_ROT_CW = {
    'B': 'L',
    'R': 'B',
    'F': 'R',
    'L': 'F',
    'S': 'Mi',
    'M': 'S',
    'Z': 'X',
    'X': 'Zi'
}
Z_ROT_CW = {
    'U': 'L',
    'R': 'U',
    'D': 'R',
    'L': 'D',
    'E': 'Mi',
    'M': 'E',
    'Y': 'Xi',
    'X': 'Y',
}
X_ROT_CC = {v: k for k, v in X_ROT_CW.items()}
Y_ROT_CC = {v: k for k, v in Y_ROT_CW.items()}
Z_ROT_CC = {v: k for k, v in Z_ROT_CW.items()}


def get_rot_table(rot):
    if rot == 'X': return X_ROT_CW
    elif rot == 'Xi': return X_ROT_CC
    elif rot == 'Y': return Y_ROT_CW
    elif rot == 'Yi': return Y_ROT_CC
    elif rot == 'Z': return Z_ROT_CW
    elif rot == 'Zi': return Z_ROT_CC


def _invert(move):
    if move.endswith('i'):
        return move[:1]
    return move + 'i'


def apply_repeat_three_optimization(moves):
    """ R, R, R --> Ri """
    changed = False
    i = 0
    while i < len(moves) - 2:
        if moves[i] == moves[i+1] == moves[i+2]:
            moves[i:i+3] = [_invert(moves[i])]
            changed = True
        else:
            i += 1
    if changed:
        apply_repeat_three_optimization(moves)


def apply_do_undo_optimization(moves):
    """ R Ri --> <nothing>, R R Ri Ri --> <nothing> """
    changed = False
    i = 0
    while i < len(moves) - 1:
        if _invert(moves[i]) == moves[i+1]:
            moves[i:i+2] = []
            changed = True
        else:
            i += 1
    if changed:
        apply_do_undo_optimization(moves)


def _unrotate(rot, moves):
    rot_table = get_rot_table(rot)
    result = []
    for move in moves:
        if move in rot_table:
            result.append(rot_table[move])
        elif _invert(move) in rot_table:
            result.append(_invert(rot_table[_invert(move)]))
        else:
            result.append(move)
    return result


def apply_no_full_cube_rotation_optimization(moves):
    rots = {'X', 'Y', 'Z', 'Xi', 'Yi', 'Zi'}
    changed = False
    i = 0
    while i < len(moves):
        if moves[i] not in rots:
            i += 1
            continue

        for j in reversed(range(i + 1, len(moves))):
            if moves[j] == _invert(moves[i]):
                moves[i:j+1] = _unrotate(moves[i], moves[i+1:j])
                changed = True
                break
        i += 1
    if changed:
        apply_no_full_cube_rotation_optimization(moves)


def optimize_moves(moves):
    result = list(moves)
    apply_no_full_cube_rotation_optimization(result)
    apply_repeat_three_optimization(result)
    apply_do_undo_optimization(result)
    return result


if __name__ == '__main__':
    test_seq_1 = ("Li Li E L Ei Li B Ei R E Ri Z E L Ei Li Zi U U Ui Ui Ui B U B B B Bi "
                  "Ri B R Z U U Ui Ui Ui B U B B B Ri B B R Bi Bi D Bi Di Z Ri B B R Bi "
                  "Bi D Bi Di Z B B Bi Ri B R Z B L Bi Li Bi Di B D B Bi Di B D B L Bi Li "
                  "Z B B B Bi Di B D B L Bi Li Z B Bi Di B D B L Bi Li Z B B B L Bi Li Bi "
                  "Di B D Z X X F F D F R Fi Ri Di Xi Xi X X Li Fi L D F Di Li F L F F Zi "
                  "Li Fi L D F Di Li F L F F Z F Li Fi L D F Di Li F L F Li Fi L D F Di "
                  "Li F L F F Xi Xi X X Ri Fi R Fi Ri F F R F F F R F Ri F R F F Ri F F F "
                  "F Ri Fi R Fi Ri F F R F F F R F Ri F R F F Ri F F Xi Xi X X R R F D Ui "
                  "R R Di U F R R R R F D Ui R R Di U F R R Z Z Z Z Z Z R R F D Ui R R Di "
                  "U F R R Z Z Z Z R R F D Ui R R Di U F R R Z Z Z Z Z Ri S Ri Ri S S Ri "
                  "Fi Fi R Si Si Ri Ri Si R Fi Fi Zi Xi Xi")
    moves = test_seq_1.split()
    print("{len(moves)} moves: {' '.join(moves)}")

    opt = optimize_moves(moves)
    print("{len(opt)} moves: {' '.join(opt)}")

    orig = cube.Cube("OOOOOOOOOYYYWWWGGGBBBYYYWWWGGGBBBYYYWWWGGGBBBRRRRRRRRR")
    c, d = cube.Cube(orig), cube.Cube(orig)

    c.sequence(" ".join(moves))
    d.sequence(" ".join(opt))
    print(c, '\n')
    print(d)
    assert c == d
