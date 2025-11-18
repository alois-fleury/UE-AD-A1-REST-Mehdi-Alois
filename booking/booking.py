from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "databases", "bookings.json")

with open(DB_PATH, "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

def write(bookings):
    with open(DB_PATH, 'w') as f:
        json.dump({"bookings": bookings}, f, indent=2)

@app.route("/bookings", methods=["GET"])
def get_bookings():
    return jsonify(bookings)

@app.route("/bookings/<userid>", methods=["GET"])
def get_booking(userid):
    for b in bookings:
        if b["userid"] == userid:
            return jsonify(b)
    return make_response(jsonify({"error": "Booking not found"}), 404)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()

    if (userid != request.args.get("uid")) and (not checkAdmin(request.args.get("uid"))) :
        return jsonify({"error": "Unauthorized"}), 403
    
    for booking in bookings:
        if booking["userid"] == userid:
            incoming_date = req["dates"][0]["date"] # On prend arbitrairement le premier élément du tableau dates
            incoming_movies = req["dates"][0]["movies"]

            for existing_date_obj in booking["dates"]:
                if existing_date_obj["date"] == incoming_date:
                    for m in incoming_movies:
                        if m not in existing_date_obj["movies"]:
                            existing_date_obj["movies"].append(m)
                    break
            else:
                booking["dates"].append(req["dates"][0])
            break
    else:
        req["userid"] = userid
        bookings.append(req)

    write(bookings)
    return make_response(jsonify({"message": "booking added"}), 200)

@app.route("/bookings/<userid>", methods=['DELETE'])
def del_booking(userid):
    incoming_date = request.args.get("date")
    movieid = request.args.get("movieid")

    if (userid != request.args.get("uid")) and (not checkAdmin(request.args.get("uid"))) :
        return jsonify({"error": "Unauthorized"}), 403

    for booking in bookings:
        if booking["userid"] == userid:
            # Suppression complète de l'utilisateur si les paramètres sont absents
            if not incoming_date and not movieid:
                bookings.remove(booking)
                write(bookings)
                return make_response(jsonify(booking), 200)

            # Suppression d'un film pour une date donnée
            if incoming_date and movieid:
                for existing_date in booking["dates"]:
                    if existing_date["date"] == incoming_date:
                        if movieid in existing_date["movies"]:
                            deleted_obj = {
                                "userid": userid,
                                "date": incoming_date,
                                "movies": [movieid]
                            }

                            existing_date["movies"].remove(movieid)

                            # On supprime la date si plus aucun film n'est réservé
                            if not existing_date["movies"]:
                                booking["dates"].remove(existing_date)
                                deleted_obj = {
                                    "userid": userid,
                                    "date": incoming_date,
                                    "movies": [movieid]
                                }

                            # On supprime la réservation si plus aucune date n'est réservée
                            if not booking["dates"]:
                                bookings.remove(booking)

                            write(bookings)
                            return make_response(jsonify(deleted_obj), 200)
                        else:
                            return make_response(jsonify({"error": f"Movie {movieid} not found for date {incoming_date}"}), 404)
                return make_response(jsonify({"error": f"Date {incoming_date} not found for user {userid}"}), 404)

            return make_response(jsonify({"error": "Both 'date' and 'movieid' must be provided"}), 400)

    return make_response(jsonify({"error": f"User {userid} not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
