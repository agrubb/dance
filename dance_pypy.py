import numpypy as np
import sys
import time

class Node(object):
    def __init__(self, key=None):
        self.key = key
        self.L = self
        self.R = self
        self.U = self
        self.D = self
        self.C = self

    def __repr__(self):
        return repr(self.key)

class DancingLinks(object):
    def __init__(self, matrix, use_greedy_column_selection=True):
        n_rows = matrix.shape[0]
        n_columns = matrix.shape[1]

        self.build_empty_columns(n_columns)
        for i, row in enumerate(matrix):
            self.insert_row(row, i)

        self.use_greedy_column_selection = use_greedy_column_selection

    def build_empty_columns(self, n_columns):
        """Build an empty dancing links structure with given # of columns"""
        self.head = Node()
        self.columns = [Node(i) for i in range(n_columns)]
        for c in self.columns:
            c.size = 0

        current = self.head
        for i in range(n_columns):
            current.R = self.columns[i]
            self.columns[i].L = current
            current = self.columns[i]

        if self.columns:
            self.columns[-1].R = self.head
            self.head.L = self.columns[-1]

    def insert_single_element(self, c, key):
        """Insert a single element at the bottom of column c"""
        node = Node(key)
        column = self.columns[c]
        column.size += 1

        node.C = column
        node.D = column
        node.U = column.U
        column.U.D = node
        column.U = node

        return node

    def insert_row(self, row, key):
        """Insert the marker for every non-zero element"""
        current = None
        first = None

        for i, v in enumerate(row):
            if v:
                node = self.insert_single_element(i, key)

                if current:
                    current.R = node
                    node.L = current
                else:
                    first = node
                current = node

        if current:
            current.R = first
            first.L = current

    def cover(self, c):
        c.R.L = c.L
        c.L.R = c.R

        i = c.D
        while i != c:
            j = i.R
            while j != i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1
                j = j.R
            i = i.D

    def uncover(self, c):
        i = c.U
        while i != c:
            j = i.L
            while j != i:
                j.C.size += 1
                j.D.U = j
                j.U.D = j
                j = j.L
            i = i.U

        c.R.L = c
        c.L.R = c

    def select_column(self):
        if not self.use_greedy_column_selection:
            return self.head.R

        best_size = sys.maxint
        best_c = None

        c = self.head.R
        while c != self.head:
            if c.size < best_size:
                best_size = c.size
                best_c = c
            c = c.R

        return best_c

    def search(self):
        if self.head.R == self.head:
            self.all_solutions.append(np.array(self.solution))
            return

        c = self.select_column()
        self.nodes_searched += 1

        self.cover(c)
        r = c.D
        while r != c:
            self.solution.append(r.key)
            j = r.R
            while j != r:
                self.cover(j.C)
                j = j.R
            self.search()
            j = r.L
            while j != r:
                self.uncover(j.C)
                j = j.L
            self.solution.pop()
            r = r.D
        self.uncover(c)

    def generate_all_solutions(self):
        self.solution = []
        self.all_solutions = []
        self.nodes_searched = 0

        start = time.clock()
        self.search()
        end = time.clock()

        print('Nodes searched: %d' % self.nodes_searched)
        print('Solutions found: %d' % len(self.all_solutions))
        print('Time elapsed: %f' % (end - start))
        return self.all_solutions

def load_problem(filename):
    f = open(filename)

    data = [[int(v) for v in line.split(" ")] for line in f]
    return np.array(data, dtype=bool)

if __name__ == '__main__':
    mat = load_problem(sys.argv[1])
    dl = DancingLinks(mat)
    solutions = dl.generate_all_solutions()

    with open(sys.argv[2], 'w') as f:
        lines = [' '.join(map(str, sol)) for sol in solutions]
        f.writelines(map(lambda s: s + '\n', lines))
