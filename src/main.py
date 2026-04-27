# %%

from collect.collect_matches import CollectorMatch
from collect.collect_details import CollectorMatchDetails
from collect.collect_leagues import CollectorLeague

from process.process_raw import LeagueProcessor, MatchDetailsProcessor

from sender.sender_s3 import S3Sender

import boto3
import pandas as pd
import sqlalchemy
from pymongo import MongoClient

import dotenv
import os

dotenv.load_dotenv()

AWS_KEY = os.getenv("AWS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

db_path = "./../data/database.db"
con = sqlalchemy.create_engine(f"sqlite:///{db_path}")

# abertura de conexão com o banco de dados do MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")

# Obtendo o database do dota
db =  client.get_database("dota2")

# Obtendo a coleção do database do dota
collection = db.get_collection("match_details")
collection.create_index("match_id", unique=True)


collector_match = CollectorMatch(engine=con)
collector_match_details = CollectorMatchDetails(sqlite_engine=con, mongodb_collection=collection )
collector_legues = CollectorLeague(engine=con)

processor_matches = MatchDetailsProcessor(collection, con)
processor_leagues = LeagueProcessor(con)


# %%


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-1'
)


# %%

print("\nColetando histórico de partidas...")

query = """
    SELECT date(max(start_time), 'unixepoch') as maxDt
    FROM match"""

dt = pd.read_sql_query(query, con)["maxDt"].astype(str).tolist()[0]

collector_match.exec_collect_until(date=dt, from_history=False)

# %%
print("\nColetando ligas...")
collector_legues.exec_collect()

# %%

print("\nColetando detalhes das partidas...")
collector_match_details.exec_all()
# %%

print("\nProcessando partidas...")
processor_matches.process_all()

print("\nProcessando ligas...")
processor_leagues.process()


print("\nEnviando dados para S3...")
sender = S3Sender(s3_client)
sender.upload_all(100000)

print("\nFim!")