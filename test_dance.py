#!/usr/bin/env python

import numpy as np
import unittest

import dance

class TestDance(unittest.TestCase):
    def test_build_data_structure(self):
        mat = np.array([[0, 0, 1, 1],
                        [1, 0, 1, 0],
                        [0, 1, 0, 0]],
                       dtype=np.bool)

        dl = dance.DancingLinks(mat)

        columns = dl.columns

        c0 = columns[0]
        c1 = columns[1]
        c2 = columns[2]
        c3 = columns[3]

        e02 = columns[2].D
        e03 = columns[3].D
        e10 = columns[0].D
        e12 = columns[2].D.D
        e21 = columns[1].D

        self.assertEqual(c0.L, dl.head)
        self.assertEqual(c0.R, c1)
        self.assertEqual(c1.L, c0)
        self.assertEqual(c1.R, c2)
        self.assertEqual(c2.L, c1)
        self.assertEqual(c2.R, c3)
        self.assertEqual(c3.L, c2)
        self.assertEqual(c3.R, dl.head)
        self.assertEqual(dl.head.L, c3)
        self.assertEqual(dl.head.R, c0)

        self.assertEqual(e02.U, c2)
        self.assertEqual(e02.D, e12)
        self.assertEqual(e02.L, e03)
        self.assertEqual(e02.R, e03)
        self.assertEqual(e02.C, c2)
        self.assertEqual(e02.key, 0)

        self.assertEqual(e03.U, c3)
        self.assertEqual(e03.D, c3)
        self.assertEqual(e03.L, e02)
        self.assertEqual(e03.R, e02)
        self.assertEqual(e03.C, c3)
        self.assertEqual(e03.key, 0)

        self.assertEqual(e10.U, c0)
        self.assertEqual(e10.D, c0)
        self.assertEqual(e10.L, e12)
        self.assertEqual(e10.R, e12)
        self.assertEqual(e10.C, c0)
        self.assertEqual(e10.key, 1)

        self.assertEqual(e12.U, e02)
        self.assertEqual(e12.D, c2)
        self.assertEqual(e12.L, e10)
        self.assertEqual(e12.R, e10)
        self.assertEqual(e12.C, c2)
        self.assertEqual(e12.key, 1)

        self.assertEqual(e21.U, c1)
        self.assertEqual(e21.D, c1)
        self.assertEqual(e21.L, e21)
        self.assertEqual(e21.R, e21)
        self.assertEqual(e21.C, c1)
        self.assertEqual(e21.key, 2)


    def test_build_data_structure_empty_row(self):
        mat = np.array([[0, 0, 1, 1],
                        [1, 0, 1, 0],
                        [0, 0, 0, 0],
                        [0, 1, 0, 0]],
                       dtype=np.bool)

        dl = dance.DancingLinks(mat)

        columns = dl.columns

        c0 = columns[0]
        c1 = columns[1]
        c2 = columns[2]
        c3 = columns[3]

        e02 = columns[2].D
        e03 = columns[3].D
        e10 = columns[0].D
        e12 = columns[2].D.D
        e31 = columns[1].D

        self.assertEqual(c0.L, dl.head)
        self.assertEqual(c0.R, c1)
        self.assertEqual(c1.L, c0)
        self.assertEqual(c1.R, c2)
        self.assertEqual(c2.L, c1)
        self.assertEqual(c2.R, c3)
        self.assertEqual(c3.L, c2)
        self.assertEqual(c3.R, dl.head)
        self.assertEqual(dl.head.L, c3)
        self.assertEqual(dl.head.R, c0)

        self.assertEqual(e02.U, c2)
        self.assertEqual(e02.D, e12)
        self.assertEqual(e02.L, e03)
        self.assertEqual(e02.R, e03)
        self.assertEqual(e02.C, c2)
        self.assertEqual(e02.key, 0)

        self.assertEqual(e03.U, c3)
        self.assertEqual(e03.D, c3)
        self.assertEqual(e03.L, e02)
        self.assertEqual(e03.R, e02)
        self.assertEqual(e03.C, c3)
        self.assertEqual(e03.key, 0)

        self.assertEqual(e10.U, c0)
        self.assertEqual(e10.D, c0)
        self.assertEqual(e10.L, e12)
        self.assertEqual(e10.R, e12)
        self.assertEqual(e10.C, c0)
        self.assertEqual(e10.key, 1)

        self.assertEqual(e12.U, e02)
        self.assertEqual(e12.D, c2)
        self.assertEqual(e12.L, e10)
        self.assertEqual(e12.R, e10)
        self.assertEqual(e12.C, c2)
        self.assertEqual(e12.key, 1)

        self.assertEqual(e31.U, c1)
        self.assertEqual(e31.D, c1)
        self.assertEqual(e31.L, e31)
        self.assertEqual(e31.R, e31)
        self.assertEqual(e31.C, c1)
        self.assertEqual(e31.key, 3)

    def test_all_solutions_1(self):
        foo = np.array([[0, 0, 1, 0, 1, 1, 0],
                        [1, 0, 0, 1, 0, 0, 1],
                        [0, 1, 1, 0, 0, 1, 0],
                        [1, 0, 0, 1, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0, 1],
                        [0, 0, 0, 1, 1, 0, 1]], dtype=np.bool)

        dl = dance.DancingLinks(foo)
        result = dl.all_solutions()

        self.assertEqual(len(result), 1)
        self.assertEqual(set(result[0]), set([0,3,4]))

    def test_all_solutions_2(self):
        foo = np.array([[0, 0, 1, 0, 1, 1, 0],
                        [1, 0, 0, 1, 0, 0, 1],
                        [0, 1, 1, 0, 0, 1, 0],
                        [0, 1, 0, 0, 0, 0, 1],
                        [0, 0, 0, 1, 1, 0, 1]], dtype=np.bool)

        dl = dance.DancingLinks(foo)
        result = dl.all_solutions()

        self.assertEqual(len(result), 0)

    def test_all_solutions_3(self):
        foo = np.array([[0, 0, 1, 0, 1, 1, 0],
                        [1, 0, 0, 1, 0, 0, 1],
                        [0, 1, 1, 0, 0, 1, 0],
                        [1, 0, 0, 1, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0, 1],
                        [0, 0, 0, 1, 1, 0, 1],
                        [0, 1, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 1, 0, 1]], dtype=np.bool)

        dl = dance.DancingLinks(foo)
        result = dl.all_solutions()

        self.assertEqual(len(result), 3)
        self.assertEqual(set([frozenset(s) for s in result]),
                         set([frozenset([0,3,4]), frozenset([0,1,6]), frozenset([2,3,7])]))

