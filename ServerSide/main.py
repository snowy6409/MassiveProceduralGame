from time import sleep
import time

import flask
from perlin_noise import PerlinNoise
from flask import Flask, jsonify
from flask import request
from tqdm import tqdm
import numpy as np

from multiprocessing import Pool

seed = 933566710
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

@app.route("/get_data")
def get_data():
    print(request.args)
    width = int(request.args["w"])
    height = int(request.args["h"])
    message = {"Map": []}

    start_time = time.time()

    axis_0 = [*range(height)]*width; axis_0.sort()
    axis_1 = [*range(width)]*height

    with Pool(16) as p:
        message["Map"] = p.starmap(generator, zip(axis_0, axis_1))

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
