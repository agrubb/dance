import numpy as np
import os
import string
import sys

def exact_cover_labels(K):
    labels = []
    for n in range(K):
        for r in range(K):
            for c in range(K):
                labels.append((n+1, r, c))

    return labels

def full_exact_cover_problem(K):
    mat = np.zeros((K*K*K, 3*K*K + K*K), dtype=np.bool)

    k = np.sqrt(K)
    boxes = np.arange(K).reshape((k,k))
    boxes = np.repeat(np.repeat(boxes, k, axis=0), k, axis=1)

    # One column for each number being in each row, column, box
    row_columns = np.arange(K) * K
    col_columns = np.arange(K) * K + K*K
    box_columns = np.arange(K) * K + 2*K*K

    # One column for each square => 1 entry per square
    sqr_columns = np.arange(K*K).reshape((K,K)) + 3*K*K

    i = 0
    for n in range(K):
        for r in range(K):
            for c in range(K):
                row_idx = row_columns[r] + n
                col_idx = col_columns[c] + n
                box_idx = box_columns[boxes[r,c]] + n
                sqr_idx = sqr_columns[r,c]

                mat[i, row_idx] = 1
                mat[i, col_idx] = 1
                mat[i, box_idx] = 1
                mat[i, sqr_idx] = 1
                i += 1

    return mat

def exact_cover_problem(board):
    if board.shape[0] != board.shape[1]:
        raise ValueError('Incorrect board shape, expected square board')
    K = board.shape[0]

    mat = full_exact_cover_problem(K)
    labels = exact_cover_labels(K)

    for r in range(K):
        for c in range(K):
            if board[r, c] > 0:
                n = board[r, c]
                mask = np.array([l[0] != n and l[1] == r and l[2] == c for l in labels], dtype=np.bool)
                mat[mask, :] = 0

    return mat

def load_solution(filename):
    solution = []
    with open(filename) as f:
        for line in f:
            solution.append(np.fromstring(line, dtype=np.int, sep=' '))

    return solution

def board_for_solution(solution, K):
    board = np.zeros((K,K), dtype=np.int)
    labels = exact_cover_labels(K)

    for row in solution:
        n = labels[row][0]
        r = labels[row][1]
        c = labels[row][2]

        board[r][c] = n

    return board

if __name__ == '__main__':
    starting_board = np.loadtxt(sys.argv[1], dtype=np.int)

    print('Generating exact cover problem...')
    mat = exact_cover_problem(starting_board)

    print('Saving to file...')
    np.savetxt('problem', mat.astype(np.int), fmt='%r')

    print('Solving exact cover problem...')
    os.spawnl(os.P_WAIT, 'dance', 'dance', 'problem', 'solution')

    solution = load_solution('solution')
    if len(solution) == 0:
        print('No solutions found!')
        sys.exit(1)

    if len(solution) > 1:
        print('Warning: solution is not unique!')

    board = board_for_solution(solution[0], starting_board.shape[0])

    print('\nSolved board is:')
    s = string.join([string.join(row.astype('S'), ' ') for row in board], '\n')
    print('%s\n' % s)

    if len(sys.argv) > 2:
        np.savetxt(sys.argv[2], board, fmt='%r')
