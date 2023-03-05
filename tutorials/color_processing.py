"""Parse the given csv files"""
from numpy import cos, sin, pi, outer, linspace, ones, inf
import plotly.graph_objects as go
import os
import pandas as pd
import numpy as np
import math
import csv

from statistics import mean, stdev


def get_rgb_data(filename, has_header=False):
    """Opens a csv file expecting rows where each row consists of numbers separated by commas (at least 3 numbers).
    Takes only the first three numbers of each row as the R,G,B values
    if has_header is True, then it will skip the first row
    """
    result = []
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(filename)
        for row in reader:
            dat = row[:3]
    if has_header:
        return result[1:]
    else:
        return result


def normalized(data):
    """Expects data to be a 2D list of RGB vectors. Returns the normalized data as a copy.
    Specifically, each inner list is a list of length 3, for Red Green and Blue values."""
    results = []
    N = len(data)
    for i in range(N):
        r, g, b = data[i]
        l = 1 / math.sqrt(r**2 + g**2 + b**2)
        results.append([r*l, g*l, b*l])
    return results


def transposed(data):
    """Takes any 2D python list and transposes it, returning a copy of the transposed list."""
    return zip(*data)


def mean2(data):
    """Takes any 2D python list and performs the mean on each row, returning a list of means of each row."""
    return [mean(row) for row in data]


def stdev2(data):
    """Takes any 2D python list and performs the mean on each row, returning a list of means of each row."""
    return [stdev(row) for row in data]


def scatter(x, y, z):
    color = ['rgb({},{},{})'.format(int(r*255), int(g*255), int(b*255)) for r, g, b in zip(x, y, z)]
    return go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=3, color=color, opacity=0.8))

def plinspace(start, stop, count):
    return [i/(count-1)*stop for i in range(start, count)]

def sphere(pos, radius, name, colors):
    """Graphs a spherical shape.
    Expects a tuple of (x,y,z) for pos and a tuple (x,y,z) for radius too."""

    theta = []
    phi = []
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

    for i in range(0,100):
        for j in range(0,100):
            x.append(p0 + cos_theta[i] * sin_phi[j])
            y.append(p1 + sin_theta[i] * sin_phi[j])
            z.append(p2 + cos_phi[i])


    data = go.Surface(
        name=name,
        x=x,
        y=y,
        z=z,
        opacity=0.5
    )
    return data


"""
========================================================


========================================================
"""
_, _, files = list(
    os.walk('./drive/My Drive/Colab Notebooks/DPM Data/csv_files'))[0]
# print(files)
sampleFile = open(
    './drive/My Drive/Colab Notebooks/DPM Data/sampleReadings.csv', 'w')
meanFile = open(
    './drive/My Drive/Colab Notebooks/DPM Data/meanReadings.csv', 'w')
sampleFile.write("Red,Green,Blue"+"\n")
meanFile.write("RedMean,GreenMean,BlueMean,RedStd,GreenStd,BlueStd"+"\n")


def normalize(red, green, blue):
    red, green, blue = list(map(float, red)), list(
        map(float, green)), list(map(float, blue))
    endR = []
    endG = []
    endB = []
    for r, g, b in zip(red, green, blue):
        endR.append(r / math.sqrt(r**2+g**2+b**2))
        endG.append(g / math.sqrt(r**2+g**2+b**2))
        endB.append(b / math.sqrt(r**2+g**2+b**2))
    return endR, endG, endB


def cleanup(red, green, blue):
    return list(map(float, red)), list(map(float, green)), list(map(float, blue))


files = [fname for fname in files if 'ColorReadings' in fname]
for fname in files:
    df = pd.read_csv(
        './drive/My Drive/Colab Notebooks/DPM Data/csv_files/'+fname)
    red, green, blue = normalize(
        df['Red'][:-2], df['Green'][:-2], df['Blue'][:-2])
    mean = [str(np.mean(red)), str(np.mean(green)), str(np.mean(blue))]
    stds = (str(np.std(red)), str(np.std(green)), str(np.std(blue)))
    red = list(map(str, red))
    green = list(map(str, green))
    blue = list(map(str, blue))
    for r, g, b in zip(red, green, blue):
        sampleFile.write(",".join([r, g, b])+"\n")
    meanFile.write(",".join(mean)+",")
    meanFile.write(",".join(stds)+"\n")
sampleFile.close()
meanFile.close()

"""Create and show the plotted data"""
# from plotly.graph_objects import *

df = pd.read_csv('./drive/My Drive/Colab Notebooks/DPM Data/meanReadings.csv')
colorMeans = [
    (0.128405,	0.035878,	0.012945, 'orange', 0.015629, 0.005528, 0.001010),
    (0.067945,	0.117534,	0.022453, 'green', 0.023059, 0.036567, 0.004786),
    (0.187547,	0.102451,	0.026272, 'yellow', 0.048666, 0.025874, 0.004234),
    (0.028634,	0.087113,	0.096172, 'blue',  0.008408, 0.016339, 0.009979),
]
stdDev = [
    list(map(float, df['RedMean'])),
    list(map(float, df['GreenMean'])),
    list(map(float, df['BlueMean'])),
    ['Distribution_'+str(i) for i in range(len(df['RedMean']))],
    list(map(float, df['RedStd'])),
    list(map(float, df['GreenStd'])),
    list(map(float, df['BlueStd']))
]
colorMeans = list(zip(*stdDev))


# df = pd.read_csv('./drive/My Drive/Colab Notebooks/DPM Data/sampleReadings_original.csv')
df = pd.read_csv(
    './drive/My Drive/Colab Notebooks/DPM Data/sampleReadings.csv')
# points = [
#   (0,0,0)
# ]

x, y, z = df['Red'], df['Green'], df['Blue']


colors = ['rgb({},{},{})'.format(int(r*256), int(g*256), int(b*256))
          for r, g, b, name, rs, gs, bs in colorMeans]
data = [sphere((r, g, b), (rs, gs, bs), name, colors)
        for r, g, b, name, rs, gs, bs in colorMeans]
data.append(scatter(x, y, z))
layout = go.Layout(
    scene=dict(
        xaxis_title='Red Value',
        yaxis_title='Green Value',
        zaxis_title='Blue Value'),
    title='Color Data Visualization',
    autosize=False,
    width=600,
    height=500
)
fig = go.Figure(data=data, layout=layout)
fig.show()
