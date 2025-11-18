from flask import Flask, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
app = Flask(__name__)

from checkAdmin import checkAdmin

PORT = 3200
HOST = '0.0.0.0'
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "databases", "movies.json")

with open(DB_PATH, 'r') as jsf:
    movies = json.load(jsf)["movies"]
    print(movies)

def write(movies):
    with open(DB_PATH, 'w') as f:
        full = {}
        full['movies']=movies
        json.dump(full, f)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# GET all movies
@app.route("/movies", methods=["GET"])
def get_movies():
    return jsonify(movies)

# GET one movie by id
@app.route("/movies/<movie_id>", methods=["GET"])
def get_movie(movie_id):
    for m in movies:
        if m["id"] == movie_id:
            return jsonify(m)
    return make_response(jsonify({"error": "Movie not found"}), 404)

@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid):
    req = request.get_json()

    if not (checkAdmin(request.args.get("uid"))):
        return jsonify({"error": "Unauthorized"}), 403

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            print(movie["id"])
            print(movieid)
            return make_response(jsonify({"error":"movie ID already exists"}),500)

    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

@app.route("/movies/<movieid>", methods=['PUT'])
def update_movie_rating(movieid):

    if not (checkAdmin(request.args.get("uid"))):
        return jsonify({"error": "Unauthorized"}), 403
    
    req = request.get_json()
    
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = req.get("rating")
            movie["title"] = req.get("title")
            res = make_response(jsonify(movie),200)
            write(movies)
            return res

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):

    if not (checkAdmin(request.args.get("uid"))):
        return jsonify({"error": "Unauthorized"}), 403
        
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            return make_response(jsonify(movie),200)

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
