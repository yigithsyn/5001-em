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
    {"id": "const", "name": "Physical constants", "modules": [
        {"id": "c0", "name": "Light in vacuum", "symbol": "c_0", "args": [], "value": eval("constants.c")}
    ]},
    {"id": "wg", "name": "Waveguide parameters", "modules": [
        {"id": "fc", "name": "Cut-off frequncy", "symbol": "f_c", "args": [
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
    module = next(module["modules"]
                  for module in modules if module["id"] == "const")
    return next(item for item in module if item["id"] == sym)

class EM_Waveguide(Resource):
  def get(self, sym):
    module = next(module["modules"]
                  for module in modules if module["id"] == "wg")
    submodule = next(item for item in module if item["id"] == sym)
    for arg in submodule["args"]:
      if arg["id"] not in request.args.keys() and not arg["optional"]:
        return {"error": ""}
      else: 
        return request.args
    return request.args 

# class TinyDB_Table(Resource):
#   def get(self, table):
#     table = tinydbDatabase.table(table)
#     items = []
#     for item in table.all():
#       item["id"] = item.doc_id
#       items.append(item)
#     return items
#   def post(self, table):
#     table = tinydbDatabase.table(table)
#     return table.insert(request.json)
#   def delete(self, table):
#     tinydbDatabase.purge_table(table)
#     return {}

# class TinyDB_Item(Resource):
#   def get(self, table, doc_id):
#     table = tinydbDatabase.table(table)
#     try:
#       item = table.get(doc_id=int(doc_id))
#       item["id"] = doc_id
#       return item
#     except Exception:
#       return {"error": {"type": "api", "msg": "TinyDB_Item: GET\n" + str(traceback.format_exc())}}
#   def post(self, table, doc_id):
#     table = tinydbDatabase.table(table)
#     try:
#       table.update(request.json, doc_ids=[int(doc_id)])
#       return {}
#     except Exception:
#       return {"error": {"type": "api", "msg": "TinyDB_Item: POST\n" + str(traceback.format_exc())}}
#   def delete(self, table, doc_id):
#     table = tinydbDatabase.table(table)
#     try:
#       table.remove(doc_ids=[int(doc_id)])
#       return {}
#     except Exception:
#       return {"error": {"type": "api", "msg": "TinyDB_Item: DEL\n" + str(traceback.format_exc())}}


api.add_resource(EM, '/em')
api.add_resource(EM_Constants, '/em/const/<sym>')
api.add_resource(EM_Waveguide, '/em/wg/<sym>')
# api.add_resource(TinyDB_Item, '/tinydb/<table>/<doc_id>')
app.run(port=5001, debug=True)
