# %%
import requests
import time

from pymongo import MongoClient

import sqlalchemy
from sqlalchemy.orm import Session

from tqdm import tqdm

from db_models import Match

# %%

db_path = "./../../data/database.db"
sqlite_engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

# abertura de conexão com o banco de dados do MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")

# Obtendo o database do dota
db =  client.get_database("dota2")

# Obtendo a coleção do database do dota
collection = db.get_collection("match_details")
collection.create_index("match_id", unique=True)

# %%

class CollectorMatchDetails:

    def __init__(self, sqlite_engine, mongodb_collection):
        self.sqlite_engine = sqlite_engine
        self.mongodb_collection = mongodb_collection
        self.url= "https://api.opendota.com/api/matches/{match_id}"


    def get_matches_to_collect(self):
        with Session(self.sqlite_engine) as session:
            matches_to_collect = (session.query(Match)
                                         .where(Match.flag_details_collected==False)
                                         .all())
        return matches_to_collect


    def get_match_details(self, match_id):
        resp = requests.get(self.url.format(match_id=match_id))
        return resp


    def transform_data(self, data):
        data["dire_logo"] = str(data.get("dire_logo", ""))
        data["radiant_logo"] = str(data.get("radiant_logo", ""))
        return data


    def insert_match_on_mongodb(self, data):
        result = self.mongodb_collection.delete_one({"match_id": data["match_id"]})
        result = self.mongodb_collection.insert_one(data)
        return result


    def update_match_as_collected(self, match_obj):
        with Session(self.sqlite_engine) as session:
            match_obj.flag_details_collected = True
            session.add(match_obj)
            session.commit()


    def exec_one(self, match_obj):
        resp = self.get_match_details(match_obj.match_id)

        if resp.status_code != 200:
            print(f"Error collecting match details for match_id {match_obj.match_id}")
            return False

        data = self.transform_data(resp.json())
        self.insert_match_on_mongodb(data)
        self.update_match_as_collected(match_obj)
        return True


    def exec_all(self):
        matches = self.get_matches_to_collect()
        for match in tqdm(matches, desc="Collecting match details"):
            if not self.exec_one(match):
                time.sleep(60)


collector = CollectorMatchDetails(sqlite_engine, collection)
collector.exec_all()

