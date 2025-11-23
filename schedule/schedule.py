from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
app = Flask(__name__)

from checkAdmin import checkAdmin
from db import get_db
from dotenv import load_dotenv
load_dotenv()

PORT = 3202
HOST = '0.0.0.0'

db = get_db()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/schedule", methods=['GET'])
def get_json():
    schedule = db.load()
    res = make_response(jsonify(schedule), 200)
    return res

@app.route("/schedule/<date>", methods=['GET'])
def get_schedule_by_date(date):
    schedule = db.load()
    for day in schedule:
        if str(day["date"]) == str(date):
            res = make_response(jsonify(day),200)
            return res
    return make_response(jsonify({"error":"Schedule day not found"}),500)

@app.route("/schedule/<date>", methods=['POST'])
def add_day(date):
    req = request.get_json()

    if not (checkAdmin(request.args.get("uid"))):
        return jsonify({"error": "Unauthorized"}), 403
    schedule = db.load()
    for day in schedule:
        if str(day["date"]) == str(date):
            print(day["date"])
            print(day)
            return make_response(jsonify({"error":"day already exists"}),500)

    schedule.append(req)
    db.write(schedule)
    res = make_response(jsonify({"message":"day added"}),200)
    return res

@app.route("/schedule/<date>", methods=['DELETE'])
def del_day(date):

    if not (checkAdmin(request.args.get("uid"))):
        return jsonify({"error": "Unauthorized"}), 403
    schedule = db.load()
    for day in schedule:
        if str(day["date"]) == str(date):
            schedule.remove(day)
            db.write(schedule)
            return make_response(jsonify(day),200)

    res = make_response(jsonify({"error":"day not found"}),500)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
