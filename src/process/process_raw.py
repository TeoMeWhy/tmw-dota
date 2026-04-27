# %%
import datetime

from sqlalchemy.orm import Session

import pandas as pd

from tqdm import tqdm

import sys
sys.path.insert(0, "../01_collect")

from db_models import db_models

# %%

class MatchDetailsProcessor:
    def __init__(self, collection, engine):
        self.collection = collection
        self.engine = engine

    def get_match_details(self, match_id):
        match_details = self.collection.find_one({"match_id": match_id})
        return match_details
              
    def extract_match_details(self, data):
        columns = [
            "version",
            "match_id",
            "leagueid",
            "start_time",
            "duration",
            "series_id",
            "series_type",
            "cluster",
            "replay_salt",
            "radiant_win",
            "pre_game_duration",
            "match_seq_num",
            "tower_status_radiant",
            "tower_status_dire",
            "barracks_status_radiant",
            "barracks_status_dire",
            "first_blood_time",
            "lobby_type",
            "human_players",
            "game_mode",
            "flags",
            "engine",
            "radiant_score",
            "dire_score",
            "radiant_team_id",
            "radiant_name",
            "radiant_logo",
            "radiant_team_complete",
            "dire_team_id",
            "dire_name",
            "dire_logo",
            "dire_team_complete",
            "radiant_captain",
            "dire_captain",
            "replay_url",
            "patch",
            "region",
        ]

        data_process = {k:data.get(k, None) for k in columns}
        
        return pd.DataFrame([pd.Series(data_process)[columns]])
        
    def save_match_details(self, df_match):
        match_id = df_match["match_id"].iloc[0]
        df_match.to_parquet(f"../data/match_details/{match_id}.parquet", index=False)

    def extract_match_player_details(self, data):
        columns = [
            "player_slot",
            "obs_placed",
            "sen_placed",
            "creeps_stacked",
            "camps_stacked",
            "rune_pickups",
            "firstblood_claimed",
            "teamfight_participation",
            "towers_killed",
            "roshans_killed",
            "observers_placed",
            "stuns",
            "kill_streaks",
            "multi_kills",
            "pred_vict",
            "account_id",
            "party_id",
            "party_size",
            "team_number",
            "team_slot",
            "hero_id",
            "hero_variant",
            "item_0",
            "item_1",
            "item_2",
            "item_3",
            "item_4",
            "item_5",
            "backpack_0",
            "backpack_1",
            "backpack_2",
            "item_neutral",
            "item_neutral2",
            "kills",
            "deaths",
            "assists",
            "leaver_status",
            "last_hits",
            "denies",
            "gold_per_min",
            "xp_per_min",
            "level",
            "net_worth",
            "aghanims_scepter",
            "aghanims_shard",
            "moonshard",
            "hero_damage",
            "tower_damage",
            "hero_healing",
            "gold",
            "gold_spent",
            "personaname",
            "name",
            "last_login",
            "rank_tier",
            "computed_mmr",
            "is_subscriber",
            "radiant_win",
            "start_time",
            "duration",
            "cluster",
            "lobby_type",
            "game_mode",
            "is_contributor",
            "patch",
            "region",
            "isRadiant",
            "win",
            "lose",
            "total_gold",
            "total_xp",
            "kills_per_min",
            "kda",
            "abandons",
            "neutral_kills",
            "tower_kills",
            "courier_kills",
            "lane_kills",
            "hero_kills",
            "observer_kills",
            "sentry_kills",
            "roshan_kills",
            "necronomicon_kills",
            "ancient_kills",
            "buyback_count",
            "observer_uses",
            "sentry_uses",
            "lane_efficiency",
            "lane_efficiency_pct",
            "lane",
            "lane_role",
            "is_roaming",
            "actions_per_min",
            "life_state_dead",
    ]

        df_template = pd.DataFrame(columns=columns)
        df_players = pd.DataFrame(data["players"])
        df = pd.concat([df_template, df_players])[columns]
        df['match_id'] = data['match_id']
        df['rank_tier'] = df['rank_tier'].astype(str).astype(float)
        return df

    def save_match_player_details(self, df_players):
        match_id = df_players["match_id"].iloc[0]
        df_players.to_parquet(f"../data/match_player_details/{match_id}.parquet", index=False)

    def process_match_id(self, match_id):
        data = self.get_match_details(match_id)
        
        df_match = self.extract_match_details(data)
        self.save_match_details(df_match)
        
        df_players = self.extract_match_player_details(data)
        self.save_match_player_details(df_players)

        return True

    def get_matches_to_process(self):
        
        query = """
        SELECT match_id
        FROM match
        WHERE flag_details_collected = 1
        AND flag_details_processed = 0"""
        
        match_ids = pd.read_sql_query(query, self.engine)["match_id"].tolist()
        return match_ids
        
    def process_all(self):
        match_ids = self.get_matches_to_process()
        for i in tqdm(match_ids):
            if self.process_match_id(match_id=i):
                with Session(self.engine) as session:
                    m = session.get(db_models.Match, i)
                    m.flag_details_processed = True
                    session.add(m)
                    session.commit()


class LeagueProcessor:

    def __init__(self, engine):
        self.engine = engine

    def get_leagues(self):
        df = pd.read_sql("SELECT * FROM league", self.engine)
        return df
    
    def save_leagues(self, df):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%s")
        df.to_parquet(f"../data/leagues/{now}.parquet", index=False)

    def process(self):
        df = self.get_leagues()
        self.save_leagues(df)

# %%
