from time import sleep

import flask
from perlin_noise import PerlinNoise
from flask import Flask, jsonify
from flask import request
from tqdm import tqdm

seed = 933566710
noise = PerlinNoise(octaves=1, seed=seed)

app = Flask(__name__)


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/get_data")
def get_data():
    print(request.args)
    width = int(request.args["w"])
    height = int(request.args["h"])
    message = {"Map": []}
    for i in (range(width)):
        for j in (range(height)):
            message["Map"].append( abs(255 * ((noise(
                [int(i) / 40, int(j) / 40])))))
        print("Row: ",i)
    response = jsonify(message=message)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(port=25567)
