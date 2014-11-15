import random
import time
from cube import Cube
import solve
from solve import Solver
from optimize import optimize_moves

SOLVED_CUBE_STR = "OOOOOOOOOYYYWWWGGGBBBYYYWWWGGGBBBYYYWWWGGGBBBRRRRRRRRR"

MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]

def random_cube():
    """
    :return: A new scrambled Cube
    """
    scramble_moves = " ".join(random.choice(MOVES) for _ in xrange(200))
    a = Cube(SOLVED_CUBE_STR)
    a.sequence(scramble_moves)
    return a

def run_case():
    C = random_cube()
    original = Cube(C)
    solver = Solver(C)
    try:
        print "Solving\n", original
        solver.solve()
    except Exception as e:
        print e

    if not C.is_solved():
        print "Failed to solve. Rerunning with DEBUG = True"
        solve.DEBUG = True
        solver = Solver(Cube(original))
        solver.solve()
    else:
        check = Cube(original)
        check.sequence(" ".join(solver.moves))
        assert check.is_solved()
        assert str(check) == SOLVED_CUBE_STR

def count_number_successful():
    successes = 0
    failures = 0

    # moves_made = []
    avg_opt_moves = 0
    avg_moves = 0
    avg_time = 0
    while True:
        C = random_cube()
        solver = Solver(C)
        try:
            start = time.time()
            solver.solve()
            duration = time.time() - start
        except Exception as e:
            pass

        if C.is_solved():
            opt_moves = optimize_moves(solver.moves)
            successes += 1
            avg_moves = (avg_moves * (successes - 1) + len(solver.moves)) / float(successes)
            avg_time = (avg_time * (successes - 1) + duration) / float(successes)
            avg_opt_moves = (avg_opt_moves * (successes - 1) + len(opt_moves)) / float(successes)
            # moves_made.append(len(solver.moves))
        else:
            failures += 1
            print "Failed (%s): %s" % (successes + failures, C.flat_str())
        total = float(successes + failures)
        if (total == 1 or total % 1000 == 0) and C.is_solved():
            print "%s: %s successes (%.3f%% passing)" % (int(total), successes, 100 * successes / total),
            print "moves=%s avg_moves=%0.3f" % (len(solver.moves), avg_moves),
            print "opt_moves=%s avg_opt_moves=%0.3f" % (len(opt_moves), avg_opt_moves),
            print "time=%0.3f avg_time=%0.3f" % (duration, avg_time)


if __name__ == '__main__':
    solve.DEBUG = False
    # run_case()
    count_number_successful()