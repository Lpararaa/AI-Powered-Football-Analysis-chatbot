import json
import os
from neo4j import GraphDatabase

# --- CONFIGURATION ---
URI = "" 
AUTH = () 

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MATCHES_FILE = os.path.join(DATA_DIR, "premier_league_23_24_matchs.json")
PLAYERS_FILE = os.path.join(DATA_DIR, "premier_league_detailed_players_23_24.json")

# --- ✅ CORRECTED MAPPING (CamelCase) ---
# Now the 'Value' (Right side) matches what your AI expects.
STAT_MAPPING = {
    # Metadata
    "minutesPlayed": "minutesPlayed",  # Changed from "minutes" to match client
    "rating": "rating",
    "is_substitute": "is_sub",         # We keep this short as per your client
    "touches": "touches",
    
    # Passing
    "totalPass": "totalPass",
    "accuratePass": "accuratePass",
    "keyPass": "keyPass",
    "totalLongBalls": "totalLongBalls",
    "accurateLongBalls": "accurateLongBalls",
    "totalCross": "totalCross",
    "accurateCross": "accurateCross",
    "bigChanceCreated": "bigChanceCreated",

    # Attacking
    "goals": "goals",
    "goalAssist": "goalAssist",
    "totalShots": "totalShots",
    "onTargetScoringAttempt": "onTargetScoringAttempt",
    "hitWoodwork": "hitWoodwork",
    "totalOffside": "totalOffside",

    # xG (Advanced)
    "expectedGoals": "expectedGoals",
    "expectedAssists": "expectedAssists",
    "expectedGoalsOnTarget": "expectedGoalsOnTarget",

    # Defense
    "totalTackle": "totalTackle",
    "wonTackle": "wonTackle",
    "interceptionWon": "interceptionWon",
    "totalClearance": "totalClearance",
    "ballRecovery": "ballRecovery",
    "duelWon": "duelWon",
    "duelLost": "duelLost",
    "aerialWon": "aerialWon",
    "aerialLost": "aerialLost",
    "errorLeadToAGoal": "errorLeadToAGoal",
    "errorLeadToAShot": "errorLeadToAShot",
    "ownGoals": "ownGoals",
    "fouls": "fouls",
    "wasFouled": "wasFouled",

    # Goalkeeper
    "saves": "saves",
    "goalsPrevented": "goalsPrevented",
    "savedShotsFromInsideTheBox": "savedShotsFromInsideTheBox",
    "punches": "punches",
    "goodHighClaim": "goodHighClaim",
    "penaltySave": "penaltySave"
}

class FootballGraph:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def load_matches(self, matches_data):
        with self.driver.session() as session:
            for match in matches_data:
                session.execute_write(self._create_match_nodes, match)
            print(f"✅ Imported {len(matches_data)} matches.")

    def load_players(self, players_data):
        with self.driver.session() as session:
            count = 0
            for p in players_data:
                session.execute_write(self._create_player_performance, p)
                count += 1
                if count % 100 == 0:
                    print(f"Processed {count} player records...", end="\r")
            print(f"\n✅ Imported {len(players_data)} player performances.")

    @staticmethod
    def _create_match_nodes(tx, m):
        # (Standard Match Import - No changes needed here)
        query = """
        MERGE (m:Match {id: $match_id})
        SET m.date = $date, m.round = $round, m.score = $score, 
            m.slug = $slug, m.status = $status
        MERGE (h:Team {name: $home_team})
        MERGE (a:Team {name: $away_team})
        MERGE (m)-[:HOME_TEAM]->(h)
        MERGE (m)-[:AWAY_TEAM]->(a)
        """
        tx.run(query, 
               match_id=m['match_id'], 
               date=m.get('date') or m.get('date_timestamp'), 
               round=m['round'],
               score=m.get('score', '0-0'), 
               slug=m.get('slug', ''),
               status=m.get('status', 'finished'),
               home_team=m['home_team'], 
               away_team=m['away_team'])

    @staticmethod
    def _create_player_performance(tx, p):
        raw_stats = p.get('statistics', {})
        
        # 1. Start with essential metadata
        # Note: We manually map 'is_substitute' to 'is_sub' here too
        relationship_props = {
            "team": p['team_name'],
            "is_sub": p.get('is_substitute', False)
        }

        # 2. Loop and Clean Keys
        for key, value in raw_stats.items():
            if isinstance(value, (dict, list)):
                continue
            
            # ✅ LOOKUP: Map raw key to CamelCase key
            # If the key isn't in our list, we use the original key.
            clean_key = STAT_MAPPING.get(key, key)
            
            relationship_props[clean_key] = value

        # 3. Save to Neo4j
        query = """
        MATCH (m:Match {id: $match_id})
        MERGE (t:Team {name: $team_name})
        MERGE (p:Player {id: $player_id})
        ON CREATE SET 
            p.name = $name, p.slug = $slug, p.position = $position, 
            p.market_value = $market_value, p.country = $country

        MERGE (p)-[r:PLAYED_IN]->(m)
        SET r += $props
        """
        
        tx.run(query, 
               match_id=p['match_id'],
               team_name=p['team_name'],
               player_id=p['player_id'],
               name=p['name'],
               slug=p['slug'],
               position=p['position'],
               market_value=p.get('market_value', 0),
               country=p.get('country', 'Unknown'),
               props=relationship_props
               )

if __name__ == "__main__":
    db = FootballGraph(URI, AUTH)

    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
            matches = json.load(f)
            print("Importing Matches...")
            db.load_matches(matches)
            
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            players = json.load(f)
            print("Importing Players...")
            db.load_players(players)
            
    db.close()