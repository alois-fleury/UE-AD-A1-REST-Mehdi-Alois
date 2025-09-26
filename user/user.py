from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

def write(users):
    with open('{}/databases/users.json'.format("."), 'w') as f:
        full = {}
        full['users'] = users
        json.dump(full, f)

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)

@app.route("/users/<user_id>", methods=["GET"])
def get_user_byid(user_id):
    for u in users :
        if u["id"] == user_id :
            return jsonify(u) 
    return make_response(jsonify({"error": "user not found"}), 404)

@app.route("/users/<userid>", methods=['POST'])
def add_movie(userid):
    req = request.get_json()

    for u in users:
        if str(u['id']) == str(userid):
            print(u['id'])
            print(userid)
            return make_response(jsonify({"error" : "user ID already exists"}),500)

    users.append(req)
    write(users)
    return make_response(jsonify({"message":"user added"}),200)
   
@app.route("/users/<userid>/<lastactive>",methods=["PUT"])
def user_update(userid,lastactive):
    for u in users : 
        if str(u["id"]) == str(userid):
            u["last_active"] = lastactive
            res = make_response(jsonify({"user updated"}),200)
            write(users)
            return res
        
    return make_response(jsonify({"user not found"}),500)

@app.route("/users/<userid>", methods=["DELETE"]) 
def user_delete(userid):
    for u in users : 
        if str(u["id"]) == userid :
            users.remove(u)
            write(users)
            return make_response(jsonify(u),200)
        
    return make_response(jsonify({"error":"user not found"}),500)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
