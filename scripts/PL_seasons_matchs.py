import time
import json
from curl_cffi import requests
import os

# Path to /data directory (relative to this script)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- CONFIGURATION ---
TOURNAMENT_ID = 17       # Premier League is always ID 17
TARGET_SEASON = "23/24"  # The specific season you requested
# ---------------------

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/",
    }

def get_season_id_for_pl():
    url = f"https://www.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/seasons"
    print(f"🔍 Looking for Season '{TARGET_SEASON}' in Premier League...")
    try:
        response = requests.get(url, headers=get_headers(), impersonate="chrome120", timeout=15)
        data = response.json()
        for season in data.get('seasons', []):
            if season['year'] == TARGET_SEASON:
                print(f"✅ Found Season ID: {season['id']}")
                return season['id']
        print(f"❌ Could not find season {TARGET_SEASON}")
        return None
    except Exception as e:
        print(f"❌ Error finding season: {e}")
        return None

def get_matches_for_round(season_id, round_num):
    url = f"https://www.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/season/{season_id}/events/round/{round_num}"
    try:
        response = requests.get(url, headers=get_headers(), impersonate="chrome120", timeout=15)
        return response.json()
    except Exception as e:
        print(f"   ⚠️ Error fetching Round {round_num}: {e}")
        return None

# --- MAIN EXECUTION ---
print(f"--- Premier League {TARGET_SEASON} Scraper ---")

season_id = get_season_id_for_pl()
all_matches = []

if season_id:
    print("\n📥 Starting Round-by-Round Extraction...")
    
    for round_num in range(1, 39):
        print(f"   > Scraping Round {round_num}/38...", end="\r")
        
        data = get_matches_for_round(season_id, round_num)
        
        if data and 'events' in data:
            for event in data['events']:
                
                # --- 🛑 FILTER LOGIC HERE ---
                status_type = event['status']['type']
                
                # If the match is postponed or canceled, skip it immediately
                if status_type == 'postponed' or status_type == 'canceled':
                    print(f"\n     ⏩ Skipping postponed match: {event['homeTeam']['name']} vs {event['awayTeam']['name']}")
                    continue 
                # ----------------------------

                match_info = {
                    "match_id": event['id'],
                    "round": round_num,
                    "date_timestamp": event.get('startTimestamp'),
                    "status": status_type,
                    "home_team": event['homeTeam']['name'],
                    "away_team": event['awayTeam']['name'],
                    "score": f"{event['homeScore'].get('display', 0)}-{event['awayScore'].get('display', 0)}"
                }
                all_matches.append(match_info)
        
        time.sleep(0.5)

    print(f"\n\n✅ Extraction Complete!")
    print(f"Total Matches Found: {len(all_matches)}")
    
    filename = "premier_league_23_24_matchs.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_matches, f, indent=4)
    print(f"📂 Saved to {filename}")

else:
    print("Script stopped: Season ID not found.")