import string
import unittest
import itertools
import traceback

import rubik.cube as cube
from rubik.cube import Cube
from rubik.maths import Point, Matrix
from rubik.solve import Solver
from rubik.optimize import *
import rubik.optimize

solved_cube_str = \
"""    UUU
    UUU
    UUU
LLL FFF RRR BBB
LLL FFF RRR BBB
LLL FFF RRR BBB
    DDD
    DDD
    DDD"""

debug_cube_str = \
"""    012
    345
    678
9ab cde fgh ijk
lmn opq rst uvw
xyz ABC DEF GHI
    JKL
    MNO
    PQR"""


class TestPoint(unittest.TestCase):

    def setUp(self):
        self.p = Point(1, 2, 3)
        self.q = Point(2, 5, 9)
        self.r = Point(2, 2, 3)

    def test_point_constructor(self):
        self.assertEqual(self.p.x, 1)
        self.assertEqual(self.p.y, 2)
        self.assertEqual(self.p.z, 3)

    def test_point_count(self):
        self.assertEqual(self.r.count(2), 2)
        self.assertEqual(self.r.count(3), 1)
        self.assertEqual(self.r.count(5), 0)
        self.assertEqual(Point(9, 9, 9).count(9), 3)

    def test_point_eq(self):
        pp = Point(self.p.x, self.p.y, self.p.z)
        self.assertEqual(self.p, pp)
        self.assertTrue(self.p == pp)
        self.assertTrue(self.p == (1, 2, 3))
        self.assertTrue(self.p == [1, 2, 3])

    def test_point_neq(self):
        points = [Point(1, 2, 3), Point(1, 2, 4), Point(1, 3, 3), Point(2, 2, 3)]
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                self.assertNotEqual(points[i], points[j])
                self.assertTrue(points[i] != points[j])
                self.assertFalse(points[i] == points[j])

    def test_point_add(self):
        self.assertEqual(self.p + self.q, Point(3, 7, 12))

    def test_point_iadd(self):
        self.p += self.q
        self.assertEqual(self.p, Point(3, 7, 12))

    def test_point_sub(self):
        self.assertEqual(self.p - self.q, Point(-1, -3, -6))

    def test_point_isub(self):
        self.p -= self.q
        self.assertEqual(self.p, Point(-1, -3, -6))

    def test_point_scale(self):
        self.assertEqual(self.p * 3, Point(3, 6, 9))

    def test_point_dot_product(self):
        self.assertEqual(self.p.dot(self.q), 39)

    def test_point_cross_produce(self):
        self.assertEqual(self.p.cross(self.q), Point(3, -3, 1))

    def test_to_tuple(self):
        self.assertEqual(tuple(self.p), (1, 2, 3))

    def test_to_list(self):
        self.assertEqual(list(self.p), [1, 2, 3])

    def test_from_tuple(self):
        self.assertEqual(Point((1, 2, 3)), self.p)

    def test_from_list(self):
        self.assertEqual(Point([1, 2, 3]), self.p)

    def test_point_str(self):
        self.assertEqual(str(self.p), "(1, 2, 3)")

    def test_point_repr(self):
        self.assertEqual(repr(self.p), "Point(1, 2, 3)")

    def test_point_iter(self):
        ii = iter(self.p)
        self.assertEqual(1, next(ii))
        self.assertEqual(2, next(ii))
        self.assertEqual(3, next(ii))
        self.assertRaises(StopIteration, ii.__next__)

    def test_point_getitem(self):
        self.assertEqual(self.p[0], 1)
        self.assertEqual(self.p[1], 2)
        self.assertEqual(self.p[2], 3)


class TestMatrix(unittest.TestCase):

    def setUp(self):
        self.A = Matrix(1, 2, 3,
                        4, 5, 6,
                        7, 8, 9)
        self.B = Matrix([9, 8, 7,
                         6, 5, 4,
                         3, 2, 1])
        self.C = Matrix([[3, 2, 1],
                         [6, 5, 4],
                         [9, 8, 7]])

        self.D = Matrix(x for x in range(11, 20))
        self.p = Point(1, 2, 3)

    def test_matrix_from_items(self):
        self.assertEqual(self.A.vals, list(range(1, 10)))

    def test_matrix_from_list(self):
        self.assertEqual(self.B.vals, list(range(9, 0, -1)))

    def test_matrix_from_nested_lists(self):
        self.assertEqual(self.C.vals, [3, 2, 1, 6, 5, 4, 9, 8, 7])

    def test_matrix_from_iterable(self):
        self.assertEqual(self.D.vals, list(range(11, 20)))

    def test_matrix_str(self):
        self.assertEqual(str(self.A), ("[1, 2, 3,\n"
                                       " 4, 5, 6,\n"
                                       " 7, 8, 9]"))

    def test_matrix_repr(self):
        self.assertEqual(repr(self.A), ("Matrix(1, 2, 3,\n"
                                        "       4, 5, 6,\n"
                                        "       7, 8, 9)"))

    def test_matrix_eq(self):
        self.assertEqual(self.A, self.A)
        self.assertEqual(self.A, Matrix(list(range(1, 10))))

    def test_matrix_add(self):
        self.assertEqual(self.A + self.D, Matrix(12, 14, 16, 18, 20, 22, 24, 26, 28))

    def test_matrix_sub(self):
        self.assertEqual(self.A - self.B, Matrix(-8, -6, -4, -2, 0, 2, 4, 6, 8))

    def test_matrix_iadd(self):
        self.A += self.D
        self.assertEqual(self.A, Matrix(12, 14, 16, 18, 20, 22, 24, 26, 28))

    def test_matrix_isub(self):
        self.A -= self.B
        self.assertEqual(self.A, Matrix(-8, -6, -4, -2, 0, 2, 4, 6, 8))

    def test_matrix_rows(self):
        self.assertEqual(list(self.A.rows()), [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_matrix_cols(self):
        self.assertEqual(list(self.A.cols()), [[1, 4, 7], [2, 5, 8], [3, 6, 9]])

    def test_matrix_point_mul(self):
        self.assertEqual(self.A * self.p, Point(14, 32, 50))

    def test_matrix_matrix_mul(self):
        self.assertEqual(self.A * self.B, Matrix(30, 24, 18, 84, 69, 54, 138, 114, 90))


class TestCube(unittest.TestCase):

    def setUp(self):
        self.solved_cube = Cube(solved_cube_str)
        self.debug_cube = Cube(debug_cube_str)

    def test_cube_constructor_solved_cube(self):
        self.assertEqual(solved_cube_str, str(self.solved_cube))

    def test_cube_constructor_unique_stickers(self):
        self.assertEqual(debug_cube_str, str(self.debug_cube))

    def test_cube_constructor_additional_whitespace(self):
        cube = Cube(" ".join(x for x in debug_cube_str))
        self.assertEqual(debug_cube_str, str(cube))

    def test_cube_copy_constructor(self):
        c = Cube(self.debug_cube)
        self.assertEqual(debug_cube_str, str(c))
        self.assertEqual(self.debug_cube, c)

    def test_cube_eq(self):
        c = Cube(debug_cube_str)
        self.assertEqual(c, self.debug_cube)
        self.assertEqual(self.debug_cube, c)

    def test_cube_neq(self):
        c = Cube(debug_cube_str)
        c.L()
        self.assertNotEqual(c, self.debug_cube)
        self.assertNotEqual(self.debug_cube, c)
        self.assertFalse(c == self.debug_cube)
        self.assertTrue(c != self.debug_cube)

    def test_cube_constructor_no_whitespace(self):
        cube = Cube("".join(x for x in debug_cube_str if x not in string.whitespace))
        self.assertEqual(debug_cube_str, str(cube))

    def test_cube_L(self):
        self.debug_cube.L()
        self.assertEqual("    I12\n"
                         "    w45\n"
                         "    k78\n"
                         "xl9 0de fgh ijP\n"
                         "yma 3pq rst uvM\n"
                         "znb 6BC DEF GHJ\n"
                         "    cKL\n"
                         "    oNO\n"
                         "    AQR",
                         str(self.debug_cube))

    def test_cube_Li(self):
        self.debug_cube.Li()
        self.assertEqual("    c12\n"
                         "    o45\n"
                         "    A78\n"
                         "bnz Jde fgh ij6\n"
                         "amy Mpq rst uv3\n"
                         "9lx PBC DEF GH0\n"
                         "    IKL\n"
                         "    wNO\n"
                         "    kQR",
                         str(self.debug_cube))

    def test_cube_R(self):
        self.debug_cube.R()
        self.assertEqual("    01e\n"
                         "    34q\n"
                         "    67C\n"
                         "9ab cdL Drf 8jk\n"
                         "lmn opO Esg 5vw\n"
                         "xyz ABR Fth 2HI\n"
                         "    JKG\n"
                         "    MNu\n"
                         "    PQi",
                         str(self.debug_cube))

    def test_cube_Ri(self):
        self.debug_cube.Ri()
        self.assertEqual("    01G\n"
                         "    34u\n"
                         "    67i\n"
                         "9ab cd2 htF Rjk\n"
                         "lmn op5 gsE Ovw\n"
                         "xyz AB8 frD LHI\n"
                         "    JKe\n"
                         "    MNq\n"
                         "    PQC",
                         str(self.debug_cube))

    def test_cube_U(self):
        self.debug_cube.U()
        self.assertEqual("    630\n"
                         "    741\n"
                         "    852\n"
                         "cde fgh ijk 9ab\n"
                         "lmn opq rst uvw\n"
                         "xyz ABC DEF GHI\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_Ui(self):
        self.debug_cube.Ui()
        self.assertEqual("    258\n"
                         "    147\n"
                         "    036\n"
                         "ijk 9ab cde fgh\n"
                         "lmn opq rst uvw\n"
                         "xyz ABC DEF GHI\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_D(self):
        self.debug_cube.D()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    678\n"
                         "9ab cde fgh ijk\n"
                         "lmn opq rst uvw\n"
                         "GHI xyz ABC DEF\n"
                         "    PMJ\n"
                         "    QNK\n"
                         "    ROL",
                         str(self.debug_cube))

    def test_cube_Di(self):
        self.debug_cube.Di()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    678\n"
                         "9ab cde fgh ijk\n"
                         "lmn opq rst uvw\n"
                         "ABC DEF GHI xyz\n"
                         "    LOR\n"
                         "    KNQ\n"
                         "    JMP",
                         str(self.debug_cube))

    def test_cube_F(self):
        self.debug_cube.F()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    znb\n"
                         "9aJ Aoc 6gh ijk\n"
                         "lmK Bpd 7st uvw\n"
                         "xyL Cqe 8EF GHI\n"
                         "    Drf\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_Fi(self):
        self.debug_cube.Fi()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    frD\n"
                         "9a8 eqC Lgh ijk\n"
                         "lm7 dpB Kst uvw\n"
                         "xy6 coA JEF GHI\n"
                         "    bnz\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_B(self):
        self.debug_cube.B()
        self.assertEqual("    htF\n"
                         "    345\n"
                         "    678\n"
                         "2ab cde fgR Gui\n"
                         "1mn opq rsQ Hvj\n"
                         "0yz ABC DEP Iwk\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    9lx",
                         str(self.debug_cube))

    def test_cube_Bi(self):
        self.debug_cube.Bi()
        self.assertEqual("    xl9\n"
                         "    345\n"
                         "    678\n"
                         "Pab cde fg0 kwI\n"
                         "Qmn opq rs1 jvH\n"
                         "Ryz ABC DE2 iuG\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    Fth",
                         str(self.debug_cube))

    def test_cube_M(self):
        self.debug_cube.M()
        self.assertEqual("    0H2\n"
                         "    3v5\n"
                         "    6j8\n"
                         "9ab c1e fgh iQk\n"
                         "lmn o4q rst uNw\n"
                         "xyz A7C DEF GKI\n"
                         "    JdL\n"
                         "    MpO\n"
                         "    PBR",
                         str(self.debug_cube))

    def test_cube_Mi(self):
        self.debug_cube.Mi()
        self.assertEqual("    0d2\n"
                         "    3p5\n"
                         "    6B8\n"
                         "9ab cKe fgh i7k\n"
                         "lmn oNq rst u4w\n"
                         "xyz AQC DEF G1I\n"
                         "    JHL\n"
                         "    MvO\n"
                         "    PjR",
                         str(self.debug_cube))

    def test_cube_E(self):
        self.debug_cube.E()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    678\n"
                         "9ab cde fgh ijk\n"
                         "uvw lmn opq rst\n"
                         "xyz ABC DEF GHI\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_Ei(self):
        self.debug_cube.Ei()
        self.assertEqual("    012\n"
                         "    345\n"
                         "    678\n"
                         "9ab cde fgh ijk\n"
                         "opq rst uvw lmn\n"
                         "xyz ABC DEF GHI\n"
                         "    JKL\n"
                         "    MNO\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_S(self):
        self.debug_cube.S()
        self.assertEqual("    012\n"
                         "    yma\n"
                         "    678\n"
                         "9Mb cde f3h ijk\n"
                         "lNn opq r4t uvw\n"
                         "xOz ABC D5F GHI\n"
                         "    JKL\n"
                         "    Esg\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_Si(self):
        self.debug_cube.Si()
        self.assertEqual("    012\n"
                         "    gsE\n"
                         "    678\n"
                         "95b cde fOh ijk\n"
                         "l4n opq rNt uvw\n"
                         "x3z ABC DMF GHI\n"
                         "    JKL\n"
                         "    amy\n"
                         "    PQR",
                         str(self.debug_cube))

    def test_cube_X(self):
        self.debug_cube.X()
        self.assertEqual("    cde\n"
                         "    opq\n"
                         "    ABC\n"
                         "bnz JKL Drf 876\n"
                         "amy MNO Esg 543\n"
                         "9lx PQR Fth 210\n"
                         "    IHG\n"
                         "    wvu\n"
                         "    kji",
                         str(self.debug_cube))

    def test_cube_Xi(self):
        self.debug_cube.Xi()
        self.assertEqual("    IHG\n"
                         "    wvu\n"
                         "    kji\n"
                         "xl9 012 htF RQP\n"
                         "yma 345 gsE ONM\n"
                         "znb 678 frD LKJ\n"
                         "    cde\n"
                         "    opq\n"
                         "    ABC",
                         str(self.debug_cube))

    def test_cube_Y(self):
        self.debug_cube.Y()
        self.assertEqual("    630\n"
                         "    741\n"
                         "    852\n"
                         "cde fgh ijk 9ab\n"
                         "opq rst uvw lmn\n"
                         "ABC DEF GHI xyz\n"
                         "    LOR\n"
                         "    KNQ\n"
                         "    JMP",
                         str(self.debug_cube))

    def test_cube_Yi(self):
        self.debug_cube.Yi()
        self.assertEqual("    258\n"
                         "    147\n"
                         "    036\n"
                         "ijk 9ab cde fgh\n"
                         "uvw lmn opq rst\n"
                         "GHI xyz ABC DEF\n"
                         "    PMJ\n"
                         "    QNK\n"
                         "    ROL",
                         str(self.debug_cube))

    def test_cube_Z(self):
        self.debug_cube.Z()
        self.assertEqual("    xl9\n"
                         "    yma\n"
                         "    znb\n"
                         "PMJ Aoc 630 kwI\n"
                         "QNK Bpd 741 jvH\n"
                         "ROL Cqe 852 iuG\n"
                         "    Drf\n"
                         "    Esg\n"
                         "    Fth",
                         str(self.debug_cube))

    def test_cube_Zi(self):
        self.debug_cube.Zi()
        self.assertEqual("    htF\n"
                         "    gsE\n"
                         "    frD\n"
                         "258 eqC LOR Gui\n"
                         "147 dpB KNQ Hvj\n"
                         "036 coA JMP Iwk\n"
                         "    bnz\n"
                         "    amy\n"
                         "    9lx",
                         str(self.debug_cube))

    def test_cube_find_face_piece(self):
        piece = self.debug_cube.find_piece('p')
        self.assertEqual(cube.FACE, piece.type)
        self.assertEqual(cube.FRONT, piece.pos)
        self.assertEqual([None, None, 'p'], piece.colors)

    def test_cube_find_edge_piece(self):
        def _check_piece(piece):
            self.assertEqual(cube.EDGE, piece.type)
            self.assertEqual(cube.FRONT + cube.UP, piece.pos)
            self.assertEqual([None, '7', 'd'], piece.colors)
        _check_piece(self.debug_cube.find_piece('d', '7'))
        _check_piece(self.debug_cube.find_piece('7', 'd'))

    def test_cube_find_corner_piece(self):
        def _check_piece(piece):
            self.assertEqual(cube.CORNER, piece.type)
            self.assertEqual(cube.FRONT + cube.UP + cube.LEFT, piece.pos)
            self.assertEqual(['b', '6', 'c'], piece.colors)
        for colors in itertools.permutations(('b', '6', 'c')):
            _check_piece(self.debug_cube.find_piece(*colors))

    def test_cube_find_face_piece_negative(self):
        self.assertIsNone(self.debug_cube.find_piece('7'))

    def test_cube_find_edge_piece_negative(self):
        self.assertIsNone(self.debug_cube.find_piece('o', 'q'))

    def test_cube_find_corner_piece_negative(self):
        self.assertIsNone(self.debug_cube.find_piece('c', '6', '9'))

    def test_cube_is_solved(self):
        self.assertTrue(self.solved_cube.is_solved())

    def test_cube_is_solved_negative(self):
        self.solved_cube.L()
        self.assertFalse(self.solved_cube.is_solved())
        self.assertFalse(self.debug_cube.is_solved())

    def test_cube_sequence(self):
        self.solved_cube.sequence("L U M Ri X E Xi Ri D D F F Bi")
        self.assertEqual("    DLU\n"
                         "    RRD\n"
                         "    FFU\n"
                         "BBL DDR BRB LDL\n"
                         "RBF RUU LFB DDU\n"
                         "FBR BBR FUD FLU\n"
                         "    DLU\n"
                         "    ULF\n"
                         "    LFR",
                         str(self.solved_cube))

    def test_cube_colors(self):
        self.assertEqual({'U', 'D', 'F', 'B', 'L', 'R'}, self.solved_cube.colors())
        debug_colors = set()
        debug_colors.update(c for c in debug_cube_str if c not in string.whitespace)
        self.assertEqual(debug_colors, self.debug_cube.colors())

    def test_cube_get_piece(self):
        piece = self.debug_cube.get_piece(0, 0, 1)
        self.assertEqual(cube.FACE, piece.type)
        self.assertEqual(cube.FRONT, piece.pos)

    def test_cube_getitem(self):
        piece = self.debug_cube[0, 0, 1]
        self.assertEqual(cube.FACE, piece.type)
        self.assertEqual(cube.FRONT, piece.pos)

    def test_cube_getitem_from_tuple(self):
        piece = self.debug_cube[(0, 0, 1)]
        self.assertEqual(cube.FACE, piece.type)
        self.assertEqual(cube.FRONT, piece.pos)

    def test_move_and_inverse(self):
        for name in ('R', 'L', 'U', 'D', 'F', 'B', 'M', 'E', 'S', 'X', 'Y', 'Z'):
            move, unmove = getattr(Cube, name), getattr(Cube, name + 'i')
            self._check_move_and_inverse(move, unmove, self.debug_cube)

    def _check_move_and_inverse(self, move, inverse, cube):
        check_str = str(cube)
        move(cube)
        self.assertNotEqual(check_str, str(cube))
        inverse(cube)
        self.assertEqual(check_str, str(cube))
        inverse(cube)
        self.assertNotEqual(check_str, str(cube))
        move(cube)
        self.assertEqual(check_str, str(cube))


class TestSolver(unittest.TestCase):

    cubes = [
        "DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR",
        "GGBYOBWBBBOYRGYOYOGWROWYWGWRBRGYBGOOGBBYOYORWWRRGRWRYW",
        "BYOYYRGOWRROWGOYWGBBGOROBWGWORBBWRWYRGYBGYWOGBROYGBWYR",
        "YWYYGWWGYBBYRRBRGWOOOYWRWRBOBYROWRGOBGRWOGWBBGBGOYYGRO",
        "ROORRYOWBWWGBYGRRBYBGGGGWWOYYBRBOWBYRWOGBYORYBOWYOGRGW"
    ]

    def test_cube_solver(self):
        for c in self.cubes:
            self._check_can_solve_cube(c)

    def _check_can_solve_cube(self, orig):
        c = Cube(orig)
        solver = Solver(c)
        try:
            solver.solve()
            self.assertTrue(c.is_solved(), msg="Failed to solve cube: " + orig)
        except Exception as e:
            self.fail(traceback.format_exc() + "original cube: " + orig)

class TestOptimize(unittest.TestCase):

    moves = (('R', 'Ri'), ('L', 'Li'), ('U', 'Ui'), ('D', 'Di'), ('F', 'Fi'), ('B', 'Bi'),
             ('M', 'Mi'), ('E', 'Ei'), ('S', 'Si'), ('X', 'Xi'), ('Y', 'Yi'), ('Z', 'Zi'))

    def test_optimize_repeat_three(self):
        for cw, cc in self.moves:
            self.assertEqual([cc], optimize_moves([cw, cw, cw]))
            self.assertEqual([cw], optimize_moves([cc, cc, cc]))
            self.assertEqual(['_', cw], optimize_moves(['_', cc, cc, cc]))
            self.assertEqual(['_', cc], optimize_moves(['_', cw, cw, cw]))
            self.assertEqual(['_', cw, '_'], optimize_moves(['_', cc, cc, cc, '_']))
            self.assertEqual(['_', cc, '_'], optimize_moves(['_', cw, cw, cw, '_']))

            self.assertEqual([cw, cw],
                              optimize_moves([cc,cc,cc, cc,cc,cc]))
            self.assertEqual([cw, cw, '_'],
                              optimize_moves([cc,cc,cc, cc,cc,cc, '_']))
            self.assertEqual([cw, cw, '_', '_'],
                              optimize_moves([cc,cc,cc, cc,cc,cc, '_','_']))
            self.assertEqual([cc],
                              optimize_moves([cc,cc,cc, cc,cc,cc, cc,cc,cc]))

    def test_optimize_do_undo(self):
        for cw, cc in self.moves:
            self.assertEqual([], optimize_moves([cc, cw]))
            self.assertEqual([], optimize_moves([cw, cc]))

            self.assertEqual([], optimize_moves([cw, cw, cc, cc]))
            self.assertEqual([], optimize_moves([cw, cw, cw, cc, cc, cc]))
            self.assertEqual([], optimize_moves([cw, cw, cw, cw, cc, cc, cc, cc]))

            self.assertEqual(['1', '2'], optimize_moves(['1', cw, cw, cc, cc, '2']))
            self.assertEqual(['1', '2', '3', '4'], optimize_moves(['1', '2', cw, cw, cc, cc, '3', '4']))

    def test_full_cube_rotation_optimization(self):
        for cw, cc in (('X', 'Xi'), ('Y', 'Yi'), ('Z', 'Zi')):
            for moves in ([cc, cw], [cw, cc]):
                rubik.optimize.apply_no_full_cube_rotation_optimization(moves)
                self.assertEqual([], moves)

        for cw, cc in (('Z', 'Zi'),):
            moves = [cw, 'U', 'L', 'D', 'R','E', 'M', cc]
            expected = ['L', 'D', 'R', 'U', 'Mi', 'E']
            actual = list(moves)
            rubik.optimize.apply_no_full_cube_rotation_optimization(actual)
            self.assertEqual(expected, actual)

            c, d = Cube(solved_cube_str), Cube(solved_cube_str)
            c.sequence(" ".join(moves))
            d.sequence(" ".join(actual))
            self.assertEqual(str(c), str(d))

            moves = [cw, cw, 'U', 'L', 'D', 'R','E', 'M', cc, cc]
            expected = ['D', 'R', 'U', 'L', 'Ei', 'Mi']
            actual = list(moves)
            rubik.optimize.apply_no_full_cube_rotation_optimization(actual)
            self.assertEqual(expected, actual)

            c, d = Cube(solved_cube_str), Cube(solved_cube_str)
            c.sequence(" ".join(moves))
            d.sequence(" ".join(actual))
            self.assertEqual(str(c), str(d))


if __name__ == '__main__':
    unittest.main()
