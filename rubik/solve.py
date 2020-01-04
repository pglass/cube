import sys
import time
from rubik import cube
from rubik.maths import Point

DEBUG = False


class Solver:

    def __init__(self, c):
        self.cube = c
        self.colors = c.colors()
        self.moves = []

        self.left_piece  = self.cube.find_piece(self.cube.left_color())
        self.right_piece = self.cube.find_piece(self.cube.right_color())
        self.up_piece    = self.cube.find_piece(self.cube.up_color())
        self.down_piece  = self.cube.find_piece(self.cube.down_color())

    def solve(self):
        if DEBUG: print(self.cube)
        self.cross()
        if DEBUG: print('Cross:\n', self.cube)
        self.cross_corners()
        if DEBUG: print('Corners:\n', self.cube)
        self.second_layer()
        if DEBUG: print('Second layer:\n', self.cube)
        self.back_face_edges()
        if DEBUG: print('Last layer edges\n', self.cube)
        self.last_layer_corners_position()
        if DEBUG: print('Last layer corners -- position\n', self.cube)
        self.last_layer_corners_orientation()
        if DEBUG: print('Last layer corners -- orientation\n', self.cube)
        self.last_layer_edges()
        if DEBUG: print('Solved\n', self.cube)

    def move(self, move_str):
        self.moves.extend(move_str.split())
        self.cube.sequence(move_str)

    def cross(self):
        if DEBUG: print("cross")
        # place the UP-LEFT piece
        fl_piece = self.cube.find_piece(self.cube.front_color(), self.cube.left_color())
        fr_piece = self.cube.find_piece(self.cube.front_color(), self.cube.right_color())
        fu_piece = self.cube.find_piece(self.cube.front_color(), self.cube.up_color())
        fd_piece = self.cube.find_piece(self.cube.front_color(), self.cube.down_color())

        self._cross_left_or_right(fl_piece, self.left_piece, self.cube.left_color(), "L L", "E L Ei Li")
        self._cross_left_or_right(fr_piece, self.right_piece, self.cube.right_color(), "R R", "Ei R E Ri")

        self.move("Z")
        self._cross_left_or_right(fd_piece, self.down_piece, self.cube.left_color(), "L L", "E L Ei Li")
        self._cross_left_or_right(fu_piece, self.up_piece, self.cube.right_color(), "R R", "Ei R E Ri")
        self.move("Zi")

    def _cross_left_or_right(self, edge_piece, face_piece, face_color, move_1, move_2):
        # don't do anything if piece is in correct place
        if (edge_piece.pos == (face_piece.pos.x, face_piece.pos.y, 1)
                and edge_piece.colors[2] == self.cube.front_color()):
            return

        # ensure piece is at z = -1
        undo_move = None
        if edge_piece.pos.z == 0:
            pos = Point(edge_piece.pos)
            pos.x = 0  # pick the UP or DOWN face
            cw, cc = cube.get_rot_from_face(pos)

            if edge_piece.pos in (cube.LEFT + cube.UP, cube.RIGHT + cube.DOWN):
                self.move(cw)
                undo_move = cc
            else:
                self.move(cc)
                undo_move = cw
        elif edge_piece.pos.z == 1:
            pos = Point(edge_piece.pos)
            pos.z = 0
            cw, cc = cube.get_rot_from_face(pos)
            self.move("{0} {0}".format(cc))
            # don't set the undo move if the piece starts out in the right position
            # (with wrong orientation) or we'll screw up the remainder of the algorithm
            if edge_piece.pos.x != face_piece.pos.x:
                undo_move = "{0} {0}".format(cw)

        assert edge_piece.pos.z == -1

        # piece is at z = -1, rotate to correct face (LEFT or RIGHT)
        count = 0
        while (edge_piece.pos.x, edge_piece.pos.y) != (face_piece.pos.x, face_piece.pos.y):
            self.move("B")
            count += 1
            if count == 10:
                raise Exception("Stuck in loop - unsolvable cube?\n" + str(self.cube))

        # if we moved a correctly-placed piece, restore it
        if undo_move:
            self.move(undo_move)

        # the piece is on the correct face on plane z = -1, but has two orientations
        if edge_piece.colors[0] == face_color:
            self.move(move_1)
        else:
            self.move(move_2)

    def cross_corners(self):
        if DEBUG: print("cross_corners")
        fld_piece = self.cube.find_piece(self.cube.front_color(), self.cube.left_color(), self.cube.down_color())
        flu_piece = self.cube.find_piece(self.cube.front_color(), self.cube.left_color(), self.cube.up_color())
        frd_piece = self.cube.find_piece(self.cube.front_color(), self.cube.right_color(), self.cube.down_color())
        fru_piece = self.cube.find_piece(self.cube.front_color(), self.cube.right_color(), self.cube.up_color())

        self.place_frd_corner(frd_piece, self.right_piece, self.down_piece, self.cube.front_color())
        self.move("Z")
        self.place_frd_corner(fru_piece, self.up_piece, self.right_piece, self.cube.front_color())
        self.move("Z")
        self.place_frd_corner(flu_piece, self.left_piece, self.up_piece, self.cube.front_color())
        self.move("Z")
        self.place_frd_corner(fld_piece, self.down_piece, self.left_piece, self.cube.front_color())
        self.move("Z")

    def place_frd_corner(self, corner_piece, right_piece, down_piece, front_color):
        # rotate to z = -1
        if corner_piece.pos.z == 1:
            pos = Point(corner_piece.pos)
            pos.x = pos.z = 0
            cw, cc = cube.get_rot_from_face(pos)

            # be careful not to screw up other pieces on the front face
            count = 0
            undo_move = cc
            while corner_piece.pos.z != -1:
                self.move(cw)
                count += 1

            if count > 1:
                # go the other direction because I don't know which is which.
                # we need to do only one flip (net) or we'll move other
                # correctly-placed corners out of place.
                for _ in range(count):
                    self.move(cc)

                count = 0
                while corner_piece.pos.z != -1:
                    self.move(cc)
                    count += 1
                undo_move = cw
            self.move("B")
            for _ in range(count):
                self.move(undo_move)

        # rotate piece to be directly below its destination
        while (corner_piece.pos.x, corner_piece.pos.y) != (right_piece.pos.x, down_piece.pos.y):
            self.move("B")

        # there are three possible orientations for a corner
        if corner_piece.colors[0] == front_color:
            self.move("B D Bi Di")
        elif corner_piece.colors[1] == front_color:
            self.move("Bi Ri B R")
        else:
            self.move("Ri B B R Bi Bi D Bi Di")

    def second_layer(self):
        rd_piece = self.cube.find_piece(self.cube.right_color(), self.cube.down_color())
        ru_piece = self.cube.find_piece(self.cube.right_color(), self.cube.up_color())
        ld_piece = self.cube.find_piece(self.cube.left_color(), self.cube.down_color())
        lu_piece = self.cube.find_piece(self.cube.left_color(), self.cube.up_color())

        self.place_middle_layer_ld_edge(ld_piece, self.cube.left_color(), self.cube.down_color())
        self.move("Z")
        self.place_middle_layer_ld_edge(rd_piece, self.cube.left_color(), self.cube.down_color())
        self.move("Z")
        self.place_middle_layer_ld_edge(ru_piece, self.cube.left_color(), self.cube.down_color())
        self.move("Z")
        self.place_middle_layer_ld_edge(lu_piece, self.cube.left_color(), self.cube.down_color())
        self.move("Z")

    def place_middle_layer_ld_edge(self, ld_piece, left_color, down_color):
        # move to z == -1
        if ld_piece.pos.z == 0:
            count = 0
            while (ld_piece.pos.x, ld_piece.pos.y) != (-1, -1):
                self.move("Z")
                count += 1

            self.move("B L Bi Li Bi Di B D")
            for _ in range(count):
                self.move("Zi")

        assert ld_piece.pos.z == -1

        if ld_piece.colors[2] == left_color:
            # left_color is on the back face, move piece to to down face
            while ld_piece.pos.y != -1:
                self.move("B")
            self.move("B L Bi Li Bi Di B D")
        elif ld_piece.colors[2] == down_color:
            # down_color is on the back face, move to left face
            while ld_piece.pos.x != -1:
                self.move("B")
            self.move("Bi Di B D B L Bi Li")
        else:
            raise Exception("BUG!!")

    def back_face_edges(self):
        # rotate BACK to FRONT
        self.move("X X")

        # States:  1     2     3     4
        #         -B-   -B-   ---   ---
        #         BBB   BB-   BBB   -B-
        #         -B-   ---   ---   ---
        def state1():
            return (self.cube[0, 1, 1].colors[2] == self.cube.front_color() and
                    self.cube[-1, 0, 1].colors[2] == self.cube.front_color() and
                    self.cube[0, -1, 1].colors[2] == self.cube.front_color() and
                    self.cube[1, 0, 1].colors[2] == self.cube.front_color())

        def state2():
            return (self.cube[0, 1, 1].colors[2] == self.cube.front_color() and
                    self.cube[-1, 0, 1].colors[2] == self.cube.front_color())

        def state3():
            return (self.cube[-1, 0, 1].colors[2] == self.cube.front_color() and
                    self.cube[1, 0, 1].colors[2] == self.cube.front_color())

        def state4():
            return (self.cube[0, 1, 1].colors[2] != self.cube.front_color() and
                    self.cube[-1, 0, 1].colors[2] != self.cube.front_color() and
                    self.cube[0, -1, 1].colors[2] != self.cube.front_color() and
                    self.cube[1, 0, 1].colors[2] != self.cube.front_color())

        count = 0
        while not state1():
            if state4() or state2():
                self.move("D F R Fi Ri Di")
            elif state3():
                self.move("D R F Ri Fi Di")
            else:
                self.move("F")
            count += 1
            if count == 10:
                raise Exception("Stuck in loop - unsolvable cube\n" + str(self.cube))

        self.move("Xi Xi")

    def last_layer_corners_position(self):
        self.move("X X")
        # UP face:
        #  4-3
        #  ---
        #  2-1
        move_1 = "Li Fi L D F Di Li F L F F "  # swaps 1 and 2
        move_2 = "F Li Fi L D F Di Li F L F "  # swaps 1 and 3

        c1 = self.cube.find_piece(self.cube.front_color(), self.cube.right_color(), self.cube.down_color())
        c2 = self.cube.find_piece(self.cube.front_color(), self.cube.left_color(), self.cube.down_color())
        c3 = self.cube.find_piece(self.cube.front_color(), self.cube.right_color(), self.cube.up_color())
        c4 = self.cube.find_piece(self.cube.front_color(), self.cube.left_color(), self.cube.up_color())

        # place corner 4
        if c4.pos == Point(1, -1, 1):
            self.move(move_1 + "Zi " + move_1 + " Z")
        elif c4.pos == Point(1, 1, 1):
            self.move("Z " + move_2 + " Zi")
        elif c4.pos == Point(-1, -1, 1):
            self.move("Zi " + move_1 + " Z")
        assert c4.pos == Point(-1, 1, 1)

        # place corner 2
        if c2.pos == Point(1, 1, 1):
            self.move(move_2 + move_1)
        elif c2.pos == Point(1, -1, 1):
            self.move(move_1)
        assert c2.pos == Point(-1, -1, 1)

        # place corner 3 and corner 1
        if c3.pos == Point(1, -1, 1):
            self.move(move_2)
        assert c3.pos == Point(1, 1, 1)
        assert c1.pos == Point(1, -1, 1)

        self.move("Xi Xi")

    def last_layer_corners_orientation(self):
        self.move("X X")

        # States:  1        2      3      4      5      6      7      8
        #           B      B             B      B        B
        #         BB-      -B-B   BBB    -BB    -BB   B-B-   B-B-B   BBB
        #         BBB      BBB    BBB    BBB    BBB    BBB    BBB    BBB
        #         -B-B     BB-    -B-    -BB    BB-B  B-B-   B-B-B   BBB
        #         B          B    B B    B               B
        def state1():
            return (self.cube[ 1,  1, 1].colors[1] == self.cube.front_color() and
                    self.cube[-1, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[0] == self.cube.front_color())

        def state2():
            return (self.cube[-1,  1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1,  1, 1].colors[0] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[1] == self.cube.front_color())

        def state3():
            return (self.cube[-1, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[-1,  1, 1].colors[2] == self.cube.front_color() and
                    self.cube[ 1,  1, 1].colors[2] == self.cube.front_color())

        def state4():
            return (self.cube[-1,  1, 1].colors[1] == self.cube.front_color() and
                    self.cube[-1, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1,  1, 1].colors[2] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[2] == self.cube.front_color())

        def state5():
            return (self.cube[-1,  1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[0] == self.cube.front_color())

        def state6():
            return (self.cube[ 1,  1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[-1, -1, 1].colors[0] == self.cube.front_color() and
                    self.cube[-1,  1, 1].colors[0] == self.cube.front_color())

        def state7():
            return (self.cube[ 1,  1, 1].colors[0] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[0] == self.cube.front_color() and
                    self.cube[-1, -1, 1].colors[0] == self.cube.front_color() and
                    self.cube[-1,  1, 1].colors[0] == self.cube.front_color())

        def state8():
            return (self.cube[ 1,  1, 1].colors[2] == self.cube.front_color() and
                    self.cube[ 1, -1, 1].colors[2] == self.cube.front_color() and
                    self.cube[-1, -1, 1].colors[2] == self.cube.front_color() and
                    self.cube[-1,  1, 1].colors[2] == self.cube.front_color())

        move_1 = "Ri Fi R Fi Ri F F R F F "
        move_2 = "R F Ri F R F F Ri F F "

        while not state8():
            if state1(): self.move(move_1)
            elif state2(): self.move(move_2)
            elif state3(): self.move(move_2 + "F F " + move_1)
            elif state4(): self.move(move_2 + move_1)
            elif state5(): self.move(move_1 + "F " + move_2)
            elif state6(): self.move(move_1 + "Fi " + move_1)
            elif state7(): self.move(move_1 + "F F " + move_1)
            else:
                self.move("F")

        # rotate corners into correct locations (cube is inverted, so swap up and down colors)
        bru_corner = self.cube.find_piece(self.cube.front_color(), self.cube.right_color(), self.cube.up_color())
        while bru_corner.pos != Point(1, 1, 1):
            self.move("F")

        self.move("Xi Xi")

    def last_layer_edges(self):
        self.move("X X")

        br_edge = self.cube.find_piece(self.cube.front_color(), self.cube.right_color())
        bl_edge = self.cube.find_piece(self.cube.front_color(), self.cube.left_color())
        bu_edge = self.cube.find_piece(self.cube.front_color(), self.cube.up_color())
        bd_edge = self.cube.find_piece(self.cube.front_color(), self.cube.down_color())

        # States:
        #       1              2
        #      ---            ---
        #      ---            ---
        #      -B-            -a-
        #  --- B-B ---    aaa BBB ---
        #  --B -B- B--    aaB -B- B--
        #  --- B-B ---    aaa B-B ---
        #      -B-            -B-
        #      ---            ---
        #      ---            ---
        #              (aB edge on any FRONT)
        def state1():
            return (bu_edge.colors[2] != self.cube.front_color() and
                    bd_edge.colors[2] != self.cube.front_color() and
                    bl_edge.colors[2] != self.cube.front_color() and
                    br_edge.colors[2] != self.cube.front_color())

        def state2():
            return (bu_edge.colors[2] == self.cube.front_color() or
                    bd_edge.colors[2] == self.cube.front_color() or
                    bl_edge.colors[2] == self.cube.front_color() or
                    br_edge.colors[2] == self.cube.front_color())


        cycle_move = "R R F D Ui R R Di U F R R"
        h_pattern_move = "Ri S Ri Ri S S Ri Fi Fi R Si Si Ri Ri Si R Fi Fi "
        fish_move = "Di Li " + h_pattern_move + " L D"

        if state1():
            # ideally, convert state1 into state2
            self._handle_last_layer_state1(br_edge, bl_edge, bu_edge, bd_edge, cycle_move, h_pattern_move)
        if state2():
            self._handle_last_layer_state2(br_edge, bl_edge, bu_edge, bd_edge, cycle_move)

        def h_pattern1():
            return (self.cube[-1,  0, 1].colors[0] != self.cube.left_color() and
                    self.cube[ 1,  0, 1].colors[0] != self.cube.right_color() and
                    self.cube[ 0, -1, 1].colors[1] == self.cube.down_color() and
                    self.cube[ 0,  1, 1].colors[1] == self.cube.up_color())

        def h_pattern2():
            return (self.cube[-1,  0, 1].colors[0] == self.cube.left_color() and
                    self.cube[ 1,  0, 1].colors[0] == self.cube.right_color() and
                    self.cube[ 0, -1, 1].colors[1] == self.cube.front_color() and
                    self.cube[ 0,  1, 1].colors[1] == self.cube.front_color())

        def fish_pattern():
            return (self.cube[cube.FRONT + cube.DOWN].colors[2] == self.cube.down_color() and
                    self.cube[cube.FRONT + cube.RIGHT].colors[2] == self.cube.right_color() and
                    self.cube[cube.FRONT + cube.DOWN].colors[1] == self.cube.front_color() and
                    self.cube[cube.FRONT + cube.RIGHT].colors[0] == self.cube.front_color())

        count = 0
        while not self.cube.is_solved():
            for _ in range(4):
                if fish_pattern():
                    self.move(fish_move)
                    if self.cube.is_solved():
                        return
                else:
                    self.move("Z")

            if h_pattern1():
                self.move(h_pattern_move)
            elif h_pattern2():
                self.move("Z " + h_pattern_move + "Zi")
            else:
                self.move(cycle_move)
            count += 1
            if count == 10:
                raise Exception("Stuck in loop - unsolvable cube:\n" + str(self.cube))

        self.move("Xi Xi")


    def _handle_last_layer_state1(self, br_edge, bl_edge, bu_edge, bd_edge, cycle_move, h_move):
        if DEBUG: print("_handle_last_layer_state1")
        def check_edge_lr():
            return self.cube[cube.LEFT + cube.FRONT].colors[2] == self.cube.left_color()

        count = 0
        while not check_edge_lr():
            self.move("F")
            count += 1
            if count == 4:
                raise Exception("Bug: Failed to handle last layer state1")

        self.move(h_move)

        for _ in range(count):
            self.move("Fi")


    def _handle_last_layer_state2(self, br_edge, bl_edge, bu_edge, bd_edge, cycle_move):
        if DEBUG: print("_handle_last_layer_state2")
        def correct_edge():
            piece = self.cube[cube.LEFT + cube.FRONT]
            if piece.colors[2] == self.cube.front_color() and piece.colors[0] == self.cube.left_color():
                return piece
            piece = self.cube[cube.RIGHT + cube.FRONT]
            if piece.colors[2] == self.cube.front_color() and piece.colors[0] == self.cube.right_color():
                return piece
            piece = self.cube[cube.UP + cube.FRONT]
            if piece.colors[2] == self.cube.front_color() and piece.colors[1] == self.cube.up_color():
                return piece
            piece = self.cube[cube.DOWN + cube.FRONT]
            if piece.colors[2] == self.cube.front_color() and piece.colors[1] == self.cube.down_color():
                return piece

        count = 0
        while True:
            edge = correct_edge()
            if edge == None:
                self.move(cycle_move)
            else:
                break

            count += 1

            if count % 3 == 0:
                self.move("Z")

            if count == 12:
                raise Exception("Stuck in loop - unsolvable cube:\n" + str(self.cube))

        while edge.pos != Point(-1, 0, 1):
            self.move("Z")

        assert self.cube[cube.LEFT + cube.FRONT].colors[2] == self.cube.front_color() and \
               self.cube[cube.LEFT + cube.FRONT].colors[0] == self.cube.left_color()


if __name__ == '__main__':
    DEBUG = True
    c = cube.Cube("DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR")
    print("Solving:\n", c)
    orig = cube.Cube(c)
    solver = Solver(c)
    solver.solve()

    print(f"{len(solver.moves)} moves: {' '.join(solver.moves)}")

    check = cube.Cube(orig)
    check.sequence(" ".join(solver.moves))
    assert check.is_solved()
