from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from checkAdmin import checkAdmin
from db import get_db
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'
MOVIE_SERVICE_URL=os.getenv("MOVIE_SERVICE_URL", "http://127.0.0.1:3200")
SCHEDULE_SERVICE_URL = os.getenv("SCHEDULE_SERVICE_URL", "http://127.0.0.1:3202")

db = get_db()

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=["GET"])
def get_bookings():
    bookings = db.load()
    return jsonify(bookings)

@app.route("/bookings/<userid>", methods=["GET"])
def get_booking(userid):
    bookings = db.load()
    for booking in bookings:
        if booking["userid"] == userid:
            dates_with_details = []
            for date in booking.get("dates"):
                movies_details = []
                for movie_id in date.get("movies", []):
                    resp = requests.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}")
                    if resp.status_code == 200:
                        movies_details.append(resp.json())
                dates_with_details.append({
                    "date": date["date"],
                    "movies": movies_details
                })
            return jsonify({"dates": dates_with_details})
    return make_response(jsonify({"error": "Booking not found"}), 404)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()

    if (userid != request.args.get("uid")) and (not checkAdmin(request.args.get("uid"))) :
        return jsonify({"error": "Unauthorized"}), 403
    bookings = db.load()

    # On considère qu'un utilisateur réserve pour aller voir un film à la fois
    incoming_date = req["dates"][0]["date"] # On prend arbitrairement le premier élément du tableau dates
    incoming_movies = req["dates"][0]["movies"]
    scheduled_response = requests.get(f"{SCHEDULE_SERVICE_URL}/schedule/{incoming_date}")
    scheduled = scheduled_response.json()
    if (not scheduled) or (scheduled.get("date", "") == ""):
        return make_response({"error": "No film scheduled on this date"}, 409)

    # Vérifie si le film est prévu à la date donnée
    scheduled_movie_ids = scheduled.get("movies", [])
    for movie_id in incoming_movies:
        if movie_id not in scheduled_movie_ids:
            return make_response({"error": "Film not scheduled for the requested date"}, 409)

    for booking in bookings:
        if booking["userid"] == userid:

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

    db.write(bookings)
    return make_response(jsonify({"message": "booking added"}), 200)

@app.route("/bookings/<userid>", methods=['DELETE'])
def del_booking(userid):
    incoming_date = request.args.get("date")
    movieid = request.args.get("movieid")

    if (userid != request.args.get("uid")) and (not checkAdmin(request.args.get("uid"))) :
        return jsonify({"error": "Unauthorized"}), 403
    bookings = db.load()
    for booking in bookings:
        if booking["userid"] == userid:
            # Suppression complète de l'utilisateur si les paramètres sont absents
            if not incoming_date and not movieid:
                bookings.remove(booking)
                db.write(bookings)
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

                            db.write(bookings)
                            return make_response(jsonify(deleted_obj), 200)
                        else:
                            return make_response(jsonify({"error": f"Movie {movieid} not found for date {incoming_date}"}), 404)
                return make_response(jsonify({"error": f"Date {incoming_date} not found for user {userid}"}), 404)

            return make_response(jsonify({"error": "Both 'date' and 'movieid' must be provided"}), 400)

    return make_response(jsonify({"error": f"User {userid} not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
