# Built-in modules
import os
import traceback
from datetime import datetime

# Installed modules
from flask import Flask, request, redirect, send_from_directory, send_file
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from scipy import constants, sqrt

# run flask app
app = Flask(__name__, static_folder='test')
CORS(app)
api = Api(app)
parser = reqparse.RequestParser()

# serve index.html


@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory("test", path)


@app.route('/')
def homepage():
    return send_from_directory("test", "index.html")


modules = [
    {"id": "const", "name": "Physical constants", "items": [
        {"id": "c0", "name": "Light in vacuum", "symbol": "c_0", "args": [], "value": eval("constants.c")}
    ]},
    {"id": "wg", "name": "Waveguide parameters", "items": [
        {"id": "fc", "name": "Cut-off frequency", "symbol": "f_c", "versions": [
            {"id": "1", "name": "TE01 mod dielectric filled waveguide", "$height": 55, "args": [
                {"id": "er", "symbol": "\\epsilon_r", "cast":"float", "name": "Dielectric coefficient of substrate"},
                {"id": "a", "symbol": "a", "cast": "float", "name": "Waveguide width"}
            ],
                "formula": "\\dfrac{1}{2\\pi\\sqrt{\\mu_0\\epsilon_0\\epsilon_r}}\\sqrt{\\dfrac{1}{a}}" +
                "= \\dfrac{c_0}{2\\pi\\sqrt{\\epsilon_r\\times a}}",
                "eval": "lambda args: constants.c/(2*constants.pi*sqrt(args[0]*args[1]))"
            }
        ]}
    ]}
]


class EM(Resource):
    def get(self):
        return modules


class EM_Constants(Resource):
    def get(self, sym):
        module = next(module["items"] for module in modules if module["id"] == "const")
        return next(item for item in module if item["id"] == sym)


class EM_Waveguide(Resource):
    def get(self, sym):
        module = next(module["items"] for module in modules if module["id"] == "wg")
        item = next(item for item in module if item["id"] == sym)
        largs = []
        for arg in item["versions"][0]["args"]:
          largs.append(eval(arg["cast"])(request.args[arg["id"]]))
        print(largs)
        # for arg in request.args:
        #   print(arg)
        return eval(item["versions"][0]["eval"])(largs)


api.add_resource(EM, '/em')
api.add_resource(EM_Constants, '/em/const/<sym>')
api.add_resource(EM_Waveguide, '/em/wg/<sym>')
app.run(port=5001)
