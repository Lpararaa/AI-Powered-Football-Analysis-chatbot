import json
import time
import os
from curl_cffi import requests
# Path to /data directory (relative to this file)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- CONFIGURATION ---
INPUT_FILE = "premier_league_23_24_matchs.json" 
# CHANGED: Replaced '/' with '_' to avoid file creation errors
OUTPUT_FILE = "premier_league_detailed_players_23_24.json"
# ---------------------

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/",
    }

def get_lineups(match_id):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/lineups"
    try:
        response = requests.get(url, headers=get_headers(), impersonate="chrome")
        if response.status_code == 200:
            return response.json()
    except:
        return None

def extract_player_details(match_id, team_name, player_entry):
    """
    Extracts the data but REMOVES 'rating' and 'ratingVersions'.
    """
    p_info = player_entry.get('player', {})
    
    # 1. Get the statistics dictionary (use .copy() to be safe)
    stats = player_entry.get('statistics', {}).copy()

    # 2. ❌ DROP THE REQUESTED KEYS
    # .pop(key, None) removes the key if it exists, does nothing if it doesn't
    stats.pop('rating', None)
    stats.pop('ratingVersions', None)

    return {
        # --- Context ---
        "match_id": match_id,
        "team_name": team_name,
        
        # --- Player Identity ---
        "player_id": p_info.get('id'),
        "name": p_info.get('name'),
        "slug": p_info.get('slug'),
        "short_name": p_info.get('shortName'),
        "country": p_info.get('country', {}).get('name'),
        "height": p_info.get('height'),
        "position": player_entry.get('position'),
        "jersey_number": player_entry.get('jerseyNumber'),
        "is_substitute": player_entry.get('substitute', False),

        # --- Market Value ---
        "market_value": p_info.get('proposedMarketValueRaw', {}).get('value'),
        "currency": p_info.get('proposedMarketValueRaw', {}).get('currency'),

        # --- MODIFIED STATISTICS (Without ratings) ---
        "statistics": stats 
    }

# --- MAIN EXECUTION ---

# 1. Load Match IDs
if not os.path.exists(INPUT_FILE):
    print(f"❌ Error: {INPUT_FILE} not found. Run the Season Scraper first.")
    exit()

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"Loaded {len(matches)} matches. Starting Deep Extraction...")
all_detailed_players = []

try:
    for index, match in enumerate(matches):
        m_id = match['match_id']
        home = match['home_team']
        away = match['away_team']
        
        # Optional: Skip postponed matches if the input file still has them
        status = match.get('status', 'finished')
        if status == 'postponed' or status == 'canceled':
             print(f"[{index+1}/{len(matches)}] ⏩ SKIPPING (Postponed): {home} vs {away}")
             continue

        print(f"[{index+1}/{len(matches)}] Fetching: {home} vs {away}...", end="\r")
        
        data = get_lineups(m_id)
        
        if data and data.get('confirmed'):
            # Process Home Team
            for p in data.get('home', {}).get('players', []):
                all_detailed_players.append(extract_player_details(m_id, home, p))
            
            # Process Away Team
            for p in data.get('away', {}).get('players', []):
                all_detailed_players.append(extract_player_details(m_id, away, p))
                
        time.sleep(1.0) # Safety delay

except KeyboardInterrupt:
    print("\n🛑 Stopped by user. Saving data...")

# Save to File
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_detailed_players, f, indent=4)

print(f"\n\n✅ Done! Saved detailed stats for {len(all_detailed_players)} players to {OUTPUT_FILE}")