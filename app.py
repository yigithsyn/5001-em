# Built-in modules
import os
import traceback
from datetime import datetime
import json

# Installed modules
from flask import Flask, request, redirect, send_from_directory, send_file
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from scipy.constants import c, pi, epsilon_0, mu_0
from scipy import sqrt

# run flask app
app = Flask(__name__, static_folder='test')
CORS(app)
api = Api(app)
parser = reqparse.RequestParser()

# serve static files
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory("test", path)


@app.route('/')
def homepage():
    return send_from_directory("test", "index.html")


with open('modules.json', encoding="utf-8") as data_file:
    modules = json.load(data_file)


class EM(Resource):
    def get(self):
        return modules


class EM_Constants(Resource):
    def get(self, sym):
        module = next(module["items"] for module in modules if module["_id"] == "const")
        return next(item["value"] for item in module if item["_id"] == sym)

class EM_Parameters(Resource):
    def get(self, mod, sym, ver):
        module = next(module["items"] for module in modules if module["_id"] == mod)
        item = next(item for item in module if item["_id"] == sym)
        if int(ver) == 0:
            return item["name"]
        largs = []
        eval_ver = item["versions"][int(ver)-1]
        for arg in eval_ver["args"]:
            largs.append(eval(arg["cast"])(request.args[arg["_id"]]))
        return eval(eval_ver["eval"])(largs)


api.add_resource(EM, '/em')
api.add_resource(EM_Constants, '/em/const/<sym>')
api.add_resource(EM_Parameters, '/em/<mod>/<sym>/<ver>')
app.run(port=5001)
