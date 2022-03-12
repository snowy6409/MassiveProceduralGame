from time import sleep
import time

import flask
from perlin_noise import PerlinNoise
from flask import Flask, jsonify
from flask import request
from tqdm import tqdm

import numpy as np
from noise import pnoise2

from multiprocessing import Pool

seed = 69
noise = PerlinNoise(octaves=1, seed=seed)

app = Flask(__name__)


@app.route("/")
def index():
    return flask.render_template("index.html")

def generator(i, j):
    n = 255 * noise([int(i) / 40, int(j) / 40])
    n = abs(n)
    return n
v_gen = np.vectorize(generator)

def generator_v2(i,j):
    return pnoise2(i / 100,
                    j / 100,
                    octaves=6,
                    persistence=0.5,
                    lacunarity=2.0,
                    repeatx=1024,
                    repeaty=1024,
                    base=seed)

def perlin_array(shape = (200, 200)):

    axis_0 = [*range(shape[0])]*shape[1]; axis_0.sort()
    axis_1 = [*range(shape[1])]*shape[0]

    with Pool(16) as p:
        arr = p.starmap(generator_v2, zip(axis_0, axis_1))

    max_arr = np.max(arr)
    min_arr = np.min(arr)
    norm_me = lambda x: (x-min_arr)/(max_arr - min_arr)
    norm_me = np.vectorize(norm_me)
    arr = norm_me(arr)

    return (255*arr.flatten()).astype("uint8").tolist()

@app.route("/get_data")
def get_data():
    print(request.args)
    width = int(request.args["w"])
    height = int(request.args["h"])
    message = {"Map": []}

    start_time = time.time()

    message["Map"] = perlin_array((height, width))

    #with Pool(16) as p:
    #    message["Map"] = p.starmap(generator, zip(axis_0, axis_1))

    #message["Map"] = list(v_gen(axis_0, axis_1, noise))
    #message["Map"] = [generator(i,j) for i,j in zip(axis_0, axis_1)]

    #for i in (range(width)):
    #    for j in (range(height)):
    #        message["Map"].append(generator(i,j))

    print("--- %s seconds ---" % (time.time() - start_time))

    response = jsonify(message=message)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(host="192.168.12.96", port=25567)
