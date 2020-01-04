import string
import textwrap

from rubik.maths import Point, Matrix

RIGHT = X_AXIS = Point(1, 0, 0)
LEFT           = Point(-1, 0, 0)
UP    = Y_AXIS = Point(0, 1, 0)
DOWN           = Point(0, -1, 0)
FRONT = Z_AXIS = Point(0, 0, 1)
BACK           = Point(0, 0, -1)

FACE = 'face'
EDGE = 'edge'
CORNER = 'corner'


# 90 degree rotations in the XY plane. CW is clockwise, CC is counter-clockwise.
ROT_XY_CW = Matrix(0, 1, 0,
                   -1, 0, 0,
                   0, 0, 1)
ROT_XY_CC = Matrix(0, -1, 0,
                   1, 0, 0,
                   0, 0, 1)

# 90 degree rotations in the XZ plane (around the y-axis when viewed pointing toward you).
ROT_XZ_CW = Matrix(0, 0, -1,
                   0, 1, 0,
                   1, 0, 0)
ROT_XZ_CC = Matrix(0, 0, 1,
                   0, 1, 0,
                   -1, 0, 0)

# 90 degree rotations in the YZ plane (around the x-axis when viewed pointing toward you).
ROT_YZ_CW = Matrix(1, 0, 0,
                   0, 0, 1,
                   0, -1, 0)
ROT_YZ_CC = Matrix(1, 0, 0,
                   0, 0, -1,
                   0, 1, 0)


def get_rot_from_face(face):
    """
    :param face: One of FRONT, BACK, LEFT, RIGHT, UP, DOWN
    :return: A pair (CW, CC) given the clockwise and counterclockwise rotations for that face
    """
    if face == RIGHT:   return "R", "Ri"
    elif face == LEFT:  return "L", "Li"
    elif face == UP:    return "U", "Ui"
    elif face == DOWN:  return "D", "Di"
    elif face == FRONT: return "F", "Fi"
    elif face == BACK:  return "B", "Bi"
    return None


class Piece:

    def __init__(self, pos, colors):
        """
        :param pos: A tuple of integers (x, y, z) each ranging from -1 to 1
        :param colors: A tuple of length three (x, y, z) where each component gives the color
            of the side of the piece on that axis (if it exists), or None.
        """
        assert all(type(x) == int and x in (-1, 0, 1) for x in pos)
        assert len(colors) == 3
        self.pos = pos
        self.colors = list(colors)
        self._set_piece_type()

    def __str__(self):
        colors = "".join(c for c in self.colors if c is not None)
        return f"({self.type}, {colors}, {self.pos})"

    def _set_piece_type(self):
        if self.colors.count(None) == 2:
            self.type = FACE
        elif self.colors.count(None) == 1:
            self.type = EDGE
        elif self.colors.count(None) == 0:
            self.type = CORNER
        else:
            raise ValueError(f"Must have 1, 2, or 3 colors - given colors={self.colors}")

    def rotate(self, matrix):
        """Apply the given rotation matrix to this piece."""
        before = self.pos
        self.pos = matrix * self.pos

        # we need to swap the positions of two things in self.colors so colors appear
        # on the correct faces. rot gives us the axes to swap between.
        rot = self.pos - before
        if not any(rot):
            return  # no change occurred
        if rot.count(0) == 2:
            rot += matrix * rot

        assert rot.count(0) == 1, (
            f"There is a bug in the Piece.rotate() method!"
            f"\nbefore: {before}"
            f"\nself.pos: {self.pos}"
            f"\nrot: {rot}"
        )

        i, j = (i for i, x in enumerate(rot) if x != 0)
        self.colors[i], self.colors[j] = self.colors[j], self.colors[i]


class Cube:
    """Stores Pieces which are addressed through an x-y-z coordinate system:
        -x is the LEFT direction, +x is the RIGHT direction
        -y is the DOWN direction, +y is the UP direction
        -z is the BACK direction, +z is the FRONT direction
    """

    def _from_cube(self, c):
        self.faces = [Piece(pos=Point(p.pos), colors=p.colors) for p in c.faces]
        self.edges = [Piece(pos=Point(p.pos), colors=p.colors) for p in c.edges]
        self.corners = [Piece(pos=Point(p.pos), colors=p.colors) for p in c.corners]
        self.pieces = self.faces + self.edges + self.corners

    def _assert_data(self):
        assert len(self.pieces) == 26
        assert all(p.type == FACE for p in self.faces)
        assert all(p.type == EDGE for p in self.edges)
        assert all(p.type == CORNER for p in self.corners)

    def __init__(self, cube_str):
        """
        cube_str looks like:
                UUU                       0  1  2
                UUU                       3  4  5
                UUU                       6  7  8
            LLL FFF RRR BBB      9 10 11 12 13 14 15 16 17 18 19 20
            LLL FFF RRR BBB     21 22 23 24 25 26 27 28 29 30 31 32
            LLL FFF RRR BBB     33 34 35 36 37 38 39 40 41 42 43 44
                DDD                      45 46 47
                DDD                      48 49 50
                DDD                      51 52 53
        Note that the back side is mirrored in the horizontal axis during unfolding.
        Each 'sticker' must be a single character.
        """
        if isinstance(cube_str, Cube):
            self._from_cube(cube_str)
            return

        cube_str = "".join(x for x in cube_str if x not in string.whitespace)
        assert len(cube_str) == 54
        self.faces = (
            Piece(pos=RIGHT, colors=(cube_str[28], None, None)),
            Piece(pos=LEFT,  colors=(cube_str[22], None, None)),
            Piece(pos=UP,    colors=(None, cube_str[4],  None)),
            Piece(pos=DOWN,  colors=(None, cube_str[49], None)),
            Piece(pos=FRONT, colors=(None, None, cube_str[25])),
            Piece(pos=BACK,  colors=(None, None, cube_str[31])))
        self.edges = (
            Piece(pos=RIGHT + UP,    colors=(cube_str[16], cube_str[5], None)),
            Piece(pos=RIGHT + DOWN,  colors=(cube_str[40], cube_str[50], None)),
            Piece(pos=RIGHT + FRONT, colors=(cube_str[27], None, cube_str[26])),
            Piece(pos=RIGHT + BACK,  colors=(cube_str[29], None, cube_str[30])),
            Piece(pos=LEFT + UP,     colors=(cube_str[10], cube_str[3], None)),
            Piece(pos=LEFT + DOWN,   colors=(cube_str[34], cube_str[48], None)),
            Piece(pos=LEFT + FRONT,  colors=(cube_str[23], None, cube_str[24])),
            Piece(pos=LEFT + BACK,   colors=(cube_str[21], None, cube_str[32])),
            Piece(pos=UP + FRONT,    colors=(None, cube_str[7], cube_str[13])),
            Piece(pos=UP + BACK,     colors=(None, cube_str[1], cube_str[19])),
            Piece(pos=DOWN + FRONT,  colors=(None, cube_str[46], cube_str[37])),
            Piece(pos=DOWN + BACK,   colors=(None, cube_str[52], cube_str[43])),
        )
        self.corners = (
            Piece(pos=RIGHT + UP + FRONT,   colors=(cube_str[15], cube_str[8], cube_str[14])),
            Piece(pos=RIGHT + UP + BACK,    colors=(cube_str[17], cube_str[2], cube_str[18])),
            Piece(pos=RIGHT + DOWN + FRONT, colors=(cube_str[39], cube_str[47], cube_str[38])),
            Piece(pos=RIGHT + DOWN + BACK,  colors=(cube_str[41], cube_str[53], cube_str[42])),
            Piece(pos=LEFT + UP + FRONT,    colors=(cube_str[11], cube_str[6], cube_str[12])),
            Piece(pos=LEFT + UP + BACK,     colors=(cube_str[9], cube_str[0], cube_str[20])),
            Piece(pos=LEFT + DOWN + FRONT,  colors=(cube_str[35], cube_str[45], cube_str[36])),
            Piece(pos=LEFT + DOWN + BACK,   colors=(cube_str[33], cube_str[51], cube_str[44])),
        )

        self.pieces = self.faces + self.edges + self.corners

        self._assert_data()

    def is_solved(self):
        def check(colors):
            assert len(colors) == 9
            return all(c == colors[0] for c in colors)
        return (check([piece.colors[2] for piece in self._face(FRONT)]) and
                check([piece.colors[2] for piece in self._face(BACK)]) and
                check([piece.colors[1] for piece in self._face(UP)]) and
                check([piece.colors[1] for piece in self._face(DOWN)]) and
                check([piece.colors[0] for piece in self._face(LEFT)]) and
                check([piece.colors[0] for piece in self._face(RIGHT)]))

    def _face(self, axis):
        """
        :param axis: One of LEFT, RIGHT, UP, DOWN, FRONT, BACK
        :return: A list of Pieces on the given face
        """
        assert axis.count(0) == 2
        return [p for p in self.pieces if p.pos.dot(axis) > 0]

    def _slice(self, plane):
        """
        :param plane: A sum of any two of X_AXIS, Y_AXIS, Z_AXIS (e.g. X_AXIS + Y_AXIS)
        :return: A list of Pieces in the given plane
        """
        assert plane.count(0) == 1
        i = next((i for i, x in enumerate(plane) if x == 0))
        return [p for p in self.pieces if p.pos[i] == 0]

    def _rotate_face(self, face, matrix):
        self._rotate_pieces(self._face(face), matrix)

    def _rotate_slice(self, plane, matrix):
        self._rotate_pieces(self._slice(plane), matrix)

    def _rotate_pieces(self, pieces, matrix):
        for piece in pieces:
            piece.rotate(matrix)

    # Rubik's Cube Notation: http://ruwix.com/the-rubiks-cube/notation/
    def L(self):  self._rotate_face(LEFT, ROT_YZ_CC)
    def Li(self): self._rotate_face(LEFT, ROT_YZ_CW)
    def R(self):  self._rotate_face(RIGHT, ROT_YZ_CW)
    def Ri(self): self._rotate_face(RIGHT, ROT_YZ_CC)
    def U(self):  self._rotate_face(UP, ROT_XZ_CW)
    def Ui(self): self._rotate_face(UP, ROT_XZ_CC)
    def D(self):  self._rotate_face(DOWN, ROT_XZ_CC)
    def Di(self): self._rotate_face(DOWN, ROT_XZ_CW)
    def F(self):  self._rotate_face(FRONT, ROT_XY_CW)
    def Fi(self): self._rotate_face(FRONT, ROT_XY_CC)
    def B(self):  self._rotate_face(BACK, ROT_XY_CC)
    def Bi(self): self._rotate_face(BACK, ROT_XY_CW)
    def M(self):  self._rotate_slice(Y_AXIS + Z_AXIS, ROT_YZ_CC)
    def Mi(self): self._rotate_slice(Y_AXIS + Z_AXIS, ROT_YZ_CW)
    def E(self):  self._rotate_slice(X_AXIS + Z_AXIS, ROT_XZ_CC)
    def Ei(self): self._rotate_slice(X_AXIS + Z_AXIS, ROT_XZ_CW)
    def S(self):  self._rotate_slice(X_AXIS + Y_AXIS, ROT_XY_CW)
    def Si(self): self._rotate_slice(X_AXIS + Y_AXIS, ROT_XY_CC)
    def X(self):  self._rotate_pieces(self.pieces, ROT_YZ_CW)
    def Xi(self): self._rotate_pieces(self.pieces, ROT_YZ_CC)
    def Y(self):  self._rotate_pieces(self.pieces, ROT_XZ_CW)
    def Yi(self): self._rotate_pieces(self.pieces, ROT_XZ_CC)
    def Z(self):  self._rotate_pieces(self.pieces, ROT_XY_CW)
    def Zi(self): self._rotate_pieces(self.pieces, ROT_XY_CC)

    def sequence(self, move_str):
        """
        :param moves: A string containing notated moves separated by spaces: "L Ri U M Ui B M"
        """
        moves = [getattr(self, name) for name in move_str.split()]
        for move in moves:
            move()

    def find_piece(self, *colors):
        if None in colors:
            return
        for p in self.pieces:
            if p.colors.count(None) == 3 - len(colors) \
                and all(c in p.colors for c in colors):
                return p

    def get_piece(self, x, y, z):
        """
        :return: the Piece at the given Point
        """
        point = Point(x, y, z)
        for p in self.pieces:
            if p.pos == point:
                return p

    def __getitem__(self, *args):
        if len(args) == 1:
            return self.get_piece(*args[0])
        return self.get_piece(*args)

    def __eq__(self, other):
        return isinstance(other, Cube) and self._color_list() == other._color_list()

    def __ne__(self, other):
        return not (self == other)

    def colors(self):
        """
        :return: A set containing the colors of all stickers on the cube
        """
        return set(c for piece in self.pieces for c in piece.colors if c is not None)

    def left_color(self): return self[LEFT].colors[0]
    def right_color(self): return self[RIGHT].colors[0]
    def up_color(self): return self[UP].colors[1]
    def down_color(self): return self[DOWN].colors[1]
    def front_color(self): return self[FRONT].colors[2]
    def back_color(self): return self[BACK].colors[2]

    def _color_list(self):
        right = [p.colors[0] for p in sorted(self._face(RIGHT), key=lambda p: (-p.pos.y, -p.pos.z))]
        left  = [p.colors[0] for p in sorted(self._face(LEFT),  key=lambda p: (-p.pos.y, p.pos.z))]
        up    = [p.colors[1] for p in sorted(self._face(UP),    key=lambda p: (p.pos.z, p.pos.x))]
        down  = [p.colors[1] for p in sorted(self._face(DOWN),  key=lambda p: (-p.pos.z, p.pos.x))]
        front = [p.colors[2] for p in sorted(self._face(FRONT), key=lambda p: (-p.pos.y, p.pos.x))]
        back  = [p.colors[2] for p in sorted(self._face(BACK),  key=lambda p: (-p.pos.y, -p.pos.x))]

        return (up + left[0:3] + front[0:3] + right[0:3] + back[0:3]
                   + left[3:6] + front[3:6] + right[3:6] + back[3:6]
                   + left[6:9] + front[6:9] + right[6:9] + back[6:9] + down)

    def flat_str(self):
        return "".join(x for x in str(self) if x not in string.whitespace)

    def __str__(self):
        template = ("    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}")

        return "    " + template.format(*self._color_list()).strip()


if __name__ == '__main__':
    cube = Cube("    DLU\n"
                "    RRD\n"
                "    FFU\n"
                "BBL DDR BRB LDL\n"
                "RBF RUU LFB DDU\n"
                "FBR BBR FUD FLU\n"
                "    DLU\n"
                "    ULF\n"
                "    LFR")
    print(cube)
