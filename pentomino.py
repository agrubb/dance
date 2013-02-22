import matplotlib.cm
import matplotlib.pyplot
import numpy as np
import os

class Piece(object):
    def __init__(self, letter, mask):
        self.letter = letter
        self.mask = mask.astype(np.bool)
        self.color = (1.0, 1.0, 1.0, 1.0)

    def unique_rotations(self):
        unique = [self.mask]

        for r in [0, 1, 2, 3]:
            for f in [0, 1]:
                rotated = self.rotation(r, f)

                is_new = True
                for u in unique:
                    if np.array_equal(u, rotated):
                        is_new = False
                        break

                if is_new:
                    unique.append(rotated)

        return unique

    def rotation(self, r, f):
        rotated = self.mask
        for i in range(r):
            rotated = np.rot90(rotated)

        if f:
            rotated = np.fliplr(rotated)
        return rotated

pieces = [Piece('P', np.array([[1, 1],
                               [1, 1],
                               [1, 0]])),
          Piece('X', np.array([[0, 1, 0],
                               [1, 1, 1],
                               [0, 1, 0]])),
          Piece('F', np.array([[0, 1, 1],
                               [1, 1, 0],
                               [0, 1, 0]])),
          Piece('V', np.array([[1, 0, 0],
                               [1, 0, 0],
                               [1, 1, 1]])),
          Piece('W', np.array([[1, 0, 0],
                               [1, 1, 0],
                               [0, 1, 1]])),
          Piece('Z', np.array([[1, 1, 0],
                               [0, 1, 0],
                               [0, 1, 1]])),
          Piece('T', np.array([[1, 1, 1],
                               [0, 1, 0],
                               [0, 1, 0]])),
          Piece('U', np.array([[1, 0, 1],
                               [1, 1, 1]])),
          Piece('V', np.array([[0, 1],
                               [1, 1],
                               [0, 1],
                               [0, 1]])),
          Piece('L', np.array([[1, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1]])),
          Piece('N', np.array([[1, 0],
                               [1, 1],
                               [0, 1],
                               [0, 1]])),
          Piece('I', np.array([[1],
                               [1],
                               [1],
                               [1],
                               [1]]))]

boards = {}
boards['hollow_chess_board'] = np.array([[1, 1, 1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 0, 0, 1, 1, 1],
                                        [1, 1, 1, 0, 0, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1, 1, 1]],
                                       dtype=np.bool)

def is_valid_location(board, mask, location):
    i, j = location
    di, dj = mask.shape

    subboard = board[i:i+di, j:j+dj]
    if subboard.shape == mask.shape and np.array_equal(mask, mask & subboard):
        return True
    else:
        return False

def valid_locations(board, mask):
    locations = [(i,j) for i in range(board.shape[0]) for j in range(board.shape[1])]
    return filter(lambda loc: is_valid_location(board, mask, loc), locations)

def fill_in_row(row, piece_index, mask, location, column_map):
    i, j = location

    row[piece_index] = True
    for r, mr in enumerate(mask):
        for c, v in enumerate(mr):
            if v:
                row[column_map[i+r, j+c]] = True

def exact_cover_problem(board):
    n_piece_columns = len(pieces)
    n_space_columns = np.nonzero(board)[0].size

    n_columns = n_piece_columns + n_space_columns

    column_map = np.cumsum(board).reshape(board.shape) + n_piece_columns - 1

    rows = []
    row_labels = []
    for piece_index, piece in enumerate(pieces):
        for mask in piece.unique_rotations():
            for location in valid_locations(board, mask):
                row = np.zeros(n_columns, dtype=np.bool)
                fill_in_row(row, piece_index, mask, location, column_map)
                rows.append(row)

    return np.array(rows, dtype=np.bool)

def exact_cover_row_labels(board):
    labels = []
    for piece_index, piece in enumerate(pieces):
        for mask_index, mask in enumerate(piece.unique_rotations()):
            for location in valid_locations(board, mask):
                labels.append((piece.letter, piece_index, mask_index, location))

    return labels

def simplified_chess_board_problems():
    base = exact_cover_problem(boards['hollow_chess_board'])
    labels = exact_cover_row_labels(boards['hollow_chess_board'])
    n_columns = base.shape[1]

    # Generate the 'X at 23' problem
    mask = np.array([l[0] == 'X' and l[3] != (0,1) for l in labels], dtype=np.bool)
    base_0 = base.copy()
    base_0[mask, :] = 0

    # Generate the 'X at 24' problem
    mask = np.array([l[0] == 'X' and l[3] != (0,2) for l in labels], dtype=np.bool)
    base_1 = base.copy()
    base_1[mask, :] = 0

    # Generate the 'X at 33, P not flipped' problem
    xmask = np.array([l[0] == 'X' and l[3] != (1,1) for l in labels], dtype=np.bool)
    pmask = np.array([l[0] == 'P' and l[2] in [0,2,4,6] for l in labels], dtype=np.bool)
    base_2 = base.copy()
    base_2[xmask, :] = 0
    base_2[pmask, :] = 0

    return base_0, base_1, base_2

def load_solution(filename):
    solution = []
    with open(filename) as f:
        for line in f:
            solution.append(np.fromstring(line, dtype=np.int, sep=' '))

    return solution

def display_solution(board, solution):
    colored = np.zeros((board.shape[0], board.shape[1], 4))
    labels = exact_cover_row_labels(board)

    for row in solution:
        l = labels[row]
        piece_index = l[1]
        mask_index = l[2]
        i, j = l[3]
        color = matplotlib.cm.rainbow(piece_index / float(len(pieces)))

        mask = pieces[piece_index].unique_rotations()[mask_index]
        for r, mr in enumerate(mask):
            for c, v in enumerate(mr):
                if v:
                    colored[i+r, j+c] = color

    matplotlib.pyplot.figure()
    matplotlib.pyplot.imshow(colored, interpolation='nearest')
    matplotlib.pyplot.axis('off')

if __name__ == '__main__':
    P1, P2, P3 = simplified_chess_board_problems()

    print('Saving subproblems...')
    np.savetxt('sub_problem_1', P1.astype(np.int), fmt='%r')
    np.savetxt('sub_problem_2', P2.astype(np.int), fmt='%r')
    np.savetxt('sub_problem_3', P3.astype(np.int), fmt='%r')

    print('Solving subproblem 1...')
    os.spawnl(os.P_WAIT, 'dance', 'dance', 'sub_problem_1', 'solution_1')

    print('Solving subproblem 2...')
    os.spawnl(os.P_WAIT, 'dance', 'dance', 'sub_problem_2', 'solution_2')

    print('Solving subproblem 3...')
    os.spawnl(os.P_WAIT, 'dance', 'dance', 'sub_problem_3', 'solution_3')

    print('Displaying first solution from each')
    solution_1 = load_solution('solution_1')
    display_solution(boards['hollow_chess_board'], solution_1[0])

    solution_2 = load_solution('solution_2')
    display_solution(boards['hollow_chess_board'], solution_2[0])

    solution_3 = load_solution('solution_3')
    display_solution(boards['hollow_chess_board'], solution_3[0])

    matplotlib.pyplot.show()
