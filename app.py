# Built-in modules
import os
import traceback
from datetime import datetime

# Installed modules
from flask import Flask, request, redirect, send_from_directory, send_file
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from scipy import constants

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
        {"id": "fc", "name": "Cut-off frequncy", "symbol": "f_c", "versions": [
            {"id": "1", "name": "TE01 mod dielectric filled waveguide", "args": [
                {"id": "a", "symbol": "a", "name": "Waveguide width"}
            ],
                "formula": "\dfrac{1}{2\pi\sqrt{\mu_0\epsilon_0\epsilon}\sqrt{\dfrac{1}{a}}}"}
        ], "args": [
            {"id": "a", "name": "Waveguide width", "optional": True, "default": 0},
            {"id": "b", "name": "Waveguide height", "optional": True, "default": 0},
            {"id": "m", "name": "First mode index", "optional": False},
            {"id": "n", "name": "Second mode index", "optional": False}
        ]}
    ]}
]


class EM(Resource):
  def get(self):
    return modules


class EM_Constants(Resource):
  def get(self, sym):
    items = next(module["item"] for module in modules if module["id"] == "const")
    return next(item for item in items if item["id"] == sym)


class EM_Waveguide(Resource):
  def get(self, sym):
    items = next(module["modules"] for module in modules if module["id"] == "wg")
    item = next(item for item in items if item["id"] == sym)
    for arg in item["args"]:
      if arg["id"] not in request.args.keys() and not arg["optional"]:
        return {"error": ""}
      else:
        return request.args
    return request.args


api.add_resource(EM, '/em')
api.add_resource(EM_Constants, '/em/const/<sym>')
api.add_resource(EM_Waveguide, '/em/wg/<sym>')
app.run(port=5001, debug=True)
