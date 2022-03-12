from time import sleep
import time

import flask
from perlin_noise import PerlinNoise
from flask import Flask, jsonify
from flask import request
from tqdm import tqdm

import numpy as np
from noise import pnoise2, pnoise3

from multiprocessing import Pool

import matplotlib.pyplot as plt

seed = 69
noise = PerlinNoise(octaves=1, seed=seed)

def generator(i, j):
    n = 255 * noise([int(i) / 40, int(j) / 40])
    n = abs(n)
    return n
v_gen = np.vectorize(generator)

def generator_v2(i,j,k):
    return pnoise3(i / 1e2,
                   j / 1e2,
                   k / 1e2,
                   octaves=1,
                   persistence=1.0,
                   lacunarity=2.0,
                   repeatx=1024,
                   repeaty=1024,
                   base=np.random.randint(100))

def perlin_array(shape = (200, 200, 200)):

    axis_0 = [*range(shape[0])]*shape[1]*shape[2]; axis_0.sort()
    axis_1 = [*range(shape[1])]*shape[2]; axis_1.sort(); axis_1*=shape[0]
    axis_2 = [*range(shape[1])]*shape[2]*shape[0]

    with Pool(16) as p:
        arr = p.starmap(generator_v2, zip(axis_0, axis_1, axis_2))

    max_arr = np.max(arr)
    min_arr = np.min(arr)
    norm_me = lambda x: (x-min_arr)/(max_arr - min_arr)
    norm_me = np.vectorize(norm_me)
    arr = norm_me(arr)
    arr = np.reshape(arr, shape)

    return (255*arr).astype("uint8")

if __name__ == '__main__':
    height = 128
    width = 128
    depth = 128

    start_time = time.time()

    ### DEPRECATED GEN METHODS ###

    # axis_0 = [*range(height)]*width; axis_0.sort()
    # axis_1 = [*range(width)]*height
    # with Pool(16) as p:
       # message["Map"] = p.starmap(generator, zip(axis_0, axis_1))

    #message["Map"] = list(v_gen(axis_0, axis_1, noise))
    #message["Map"] = [generator(i,j) for i,j in zip(axis_0, axis_1)]

    #for i in (range(width)):
    #    for j in (range(height)):
    #        message["Map"].append(generator(i,j))

    ### END ###

    Map = perlin_array((height, width, depth))
    print("--- %s seconds ---" % (time.time() - start_time))
    print(Map)

    # Controll Tranperency
    alpha = 0.0
      
    # Control colour
    colors = np.empty([height, width, depth] + [4], dtype=np.float32)
    colors[Map>=0] = [0, 0.5, 1, 0.75]
    Map[Map<=128] = 0

    fig = plt.figure()
    ax = plt.axes(projection ='3d')
    ax.voxels(Map, facecolors=colors)
    plt.show()