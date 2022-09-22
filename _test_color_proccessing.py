import unittest
from numpy import cos, sin, pi, outer, linspace, ones, inf
import plotly.graph_objects as go
import os
import pandas as pd
import numpy as np
import math
import csv

from statistics import mean, stdev

import sys

def sphere_np(pos, radius):
    theta = linspace(0, 2*pi, 100)
    phi = linspace(0, pi, 100)
    x = pos[0]+outer(radius[0]*2*cos(theta), sin(phi))
    y = pos[1]+outer(radius[1]*2*sin(theta), sin(phi))
    z = pos[2]+outer(ones(100), radius[2]*2*cos(phi))  # note this is 2d now
    return x, y, z


def plinspace(start, stop, count):
    return [i/(count-1)*stop for i in range(start, count)]


def sphere_py(pos, radius):
    sin_phi = []
    cos_theta = []
    sin_theta = []
    cos_phi = []
    r0, r1, r2 = radius
    p0, p1, p2 = pos
    for phi in plinspace(0, math.pi, 100):
        theta = phi*2
        cos_theta.append(r0*2*math.cos(theta))
        sin_theta.append(r1*2*math.sin(theta))
        cos_phi.append(r2*2*math.cos(phi))
        sin_phi.append(math.sin(phi))
    x = []
    y = []
    z = []

    for i in range(0, 100):
        x_row = []
        y_row = []
        z_row = []

        for j in range(0, 100):
            x_row.append(p0 + cos_theta[i] * sin_phi[j])
            y_row.append(p1 + sin_theta[i] * sin_phi[j])
            z_row.append(p2 + cos_phi[i])

        x.append(x_row)
        y.append(y_row)
        z.append(z_row)

    return x, y, z


class TestSuperCase(unittest.TestCase):
    def assertAlmostEqual1(self, lst1, lst2):
        self.assertEqual(len(lst1), len(lst2))
        N = len(lst1)
        for i in range(N):
            try:
                self.assertAlmostEqual(lst1[i], lst2[i], places=1)
            except Exception as err:
                print(lst1[i], lst2[i], file=sys.stderr)
                raise err

    def assertAlmostEqual2(self, lst1, lst2):
        self.assertEqual(len(lst1), len(lst2))
        N = len(lst1)
        for i in range(N):
            self.assertEqual(len(lst1[i]), len(lst2[i]))
            self.assertAlmostEqual1(lst1[i], lst2[i])

    def assertAlmostEqual3(self, lst1, lst2):
        self.assertEqual(len(lst1), len(lst2))
        N = len(lst1)
        for i in range(N):
            self.assertEqual(len(lst1), len(lst2))
            self.assertAlmostEqual2(lst1[i], lst2[i])


class TestSphere(TestSuperCase):
    def test_00(self):
        self.assertAlmostEqual1(linspace(0, 2*pi, 100),
                                plinspace(0, 2*pi, 100))

    def test_01(self):
        pos = [1, 2, 3]
        radius = [5, 5, 5]
        self.assertAlmostEqual3(sphere_np(pos, radius), sphere_py(pos, radius))


if __name__ == '__main__':
    unittest.main()
