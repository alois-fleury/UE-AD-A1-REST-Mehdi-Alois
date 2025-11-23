import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

USE_MONGO = os.getenv("USING_MONGO", "false").lower() == "true"
MONGO_URL = os.getenv("DB_URL")
DB_PATH = os.getenv("DB_PATH", "./databases/bookings.json")


# -------- JSON BACKEND --------

class DbJson:
    def load(self):
        with open(DB_PATH, "r") as f:
            return json.load(f)["bookings"]

    def write(self, bookings):
        with open(DB_PATH, "w") as f:
            json.dump({"bookings": bookings}, f)


# -------- MONGO BACKEND --------

class DbMongo:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_default_database()
        self.col = self.db["bookings"]

        # initialise Mongo depuis le JSON si vide
        if self.col.count_documents({}) == 0:
            json_db = DbJson()
            initial = json_db.load()
            if initial:
                self.col.insert_many(initial)

    def load(self):
        # projection pour retirer _id
        return list(self.col.find({}, {"_id": 0}))

    def write(self, bookings):
        self.col.delete_many({})
        if bookings:
            self.col.insert_many(bookings)


# -------- SELECT BACKEND --------

def get_db():
    return DbMongo() if USE_MONGO else DbJson()
