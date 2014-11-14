# Overview

This a Python implementation of a Rubik's Cube solver.
 
## Implementation

### Piece

The cornerstone of this implementation is the Piece class. A Piece stores two pieces of information:

1. An integer `position` vector `(x, y, z)` where each component is in {-1, 0, 1}:
	- `(0, 0, 0)` is the center of the cube
	- the positive x-axis points to the right face
	- the positive y-axis points to the up face
	- the positive z-axis points to the front face

2. A `colors` vector `(cx, cy, cz)`, giving the color of the sticker along each axis. Null values are place whenever that Piece has less than three sides. For example, a Piece with `colors=('Orange', None, 'Red')` is an edge piece with an `'Orange'` sticker facing the x-direction and a `'Red'` sticker facing the z-direction. The Piece doesn't know or care which direction along the x-axis the `'Orange'` sticker is facing, just that it is facing in the x-direction and not the y- or z- directions.

Using the combination of `position` and `color` vectors makes it easy to identify any Piece by its absolute position or by its unique combination of colors.

A Piece provides a method `Piece.rotate(matrix)`, which accepts a (90 degree) rotation matrix. A matrix-vector multiplication is done to update the Piece's `position` vector. Then we update the `colors` vector, by swapping exactly two entries in the `colors` vector:

- For example, a corner Piece has three stickers of different colors. After a 90 degree rotation of the Piece, one sticker remains facing down the same axis, while the other two stickers swap axes. This corresponds to swapping the positions of two entries in the Piece’s `colors` vector.
- For an edge or face piece, the argument is the same as above, although we may swap around one or more null entries.

### Cube

The crux of the Cube implementation is the Piece class. The Cube simply stores a list of Pieces and provides nice methods for flipping slices of the cube, as well as methods for querying the current state. (I followed standard [Rubik's Cube notation](http://ruwix.com/the-rubiks-cube/notation/))

Because the Piece class encapsulates all of the rotation logic, implementing rotations in the Cube class is dead simple - just apply the appropriate rotation matrix to all Pieces involved in the rotation. An example: To implement `Cube.L()` - a clockwise rotation of the left face - do the following:

1. Construct the appropriate [rotation matrix](http://en.wikipedia.org/wiki/Rotation_matrix) for a 90 degree rotation in the `x = -1` plane.
2. Select all Pieces satisfying `position.x == -1`.
3. Apply the rotation matrix to each of these Pieces.

To implement `Cube.X()` - a clockwise rotation of the *entire* cube around the positive x-axis - just apply a rotation matrix to all Pieces stored in the Cube.

### Solver

The solver implements the algorithm described [here](http://peter.stillhq.com/jasmine/rubikscubesolution.html) and [here](http://www.chessandpoker.com/rubiks-cube-solution.html). It is a layer-by-layer solution. First the front-face (the `z = 1` plane) is solved, then the middle layer (`z = 0`), and finally the back layer (`z = 0`). When the solver is done, `Solver.moves` is a list representing the solution sequence.

My first complete implementation of the solver produced no failures and averaged 252.5 moves per solution sequence on 135000 randomly-generated cubes.