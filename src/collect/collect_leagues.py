# %%
import requests

from sqlalchemy.orm import Session
from db_models import db_models


# %%

class CollectorLeague:

    def __init__(self, engine):
        self.engine = engine
        self.url = "https://api.opendota.com/api/leagues"

    def get_leagues(self):
        resp = requests.get(self.url)
        return resp
    
    def save_leagues(self, data):
        leagues = []

        with Session(self.engine) as session:
            for d in data:
                
                league = session.get(db_models.League, d["leagueid"])
                if not league:
                    league = db_models.League(**d)
            
                leagues.append(league)

            session.add_all(leagues)
            session.commit()
            return True


    def exec_collect(self):
        resp = self.get_leagues()
        if resp.status_code != 200:
            return False
        return self.save_leagues(resp.json())


