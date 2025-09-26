from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

def write(schedule):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule']=schedule
        json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(schedule), 200)
    return res

@app.route("/schedule/<date>", methods=['GET'])
def get_schedule_by_date(date):
    for day in schedule:
        if str(day["date"]) == str(date):
            res = make_response(jsonify(day),200)
            return res
    return make_response(jsonify({"error":"Schedule day not found"}),500)

@app.route("/schedule/<date>", methods=['POST'])
def add_day(date):
    req = request.get_json()

    for day in schedule:
        if str(day["date"]) == str(date):
            print(day["date"])
            print(day)
            return make_response(jsonify({"error":"day already exists"}),500)

    schedule.append(req)
    write(schedule)
    res = make_response(jsonify({"message":"day added"}),200)
    return res

@app.route("/schedule/<date>", methods=['DELETE'])
def del_day(date):
    for day in schedule:
        if str(day["date"]) == str(date):
            schedule.remove(day)
            write(schedule)
            return make_response(jsonify(day),200)

    res = make_response(jsonify({"error":"day not found"}),500)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
