import requests
import pandas as pd
from datetime import datetime

# Your configured keys
CFBD_API_KEY = "BotEtAGH7nFzBkEwWJvCk8x6vT2gIEXfLBKvGgtC6IEv/2sa0ag79IMI6STxVpFK"
ODDS_API_KEY = "8a4959f73ddff1b6d07524bb82307d76"

CURRENT_YEAR = 2026
CURRENT_WEEK = 5

def main():
    print(f"Fetching Week {CURRENT_WEEK} data...")
    
    # 1. Fetch CFBD games
    url_cfbd = "https://api.collegefootballdata.com/games"
    headers = {"Authorization": f"Bearer {CFBD_API_KEY}", "accept": "application/json"}
    params_cfbd = {"year": CURRENT_YEAR, "week": CURRENT_WEEK, "seasonType": "regular"}
    res_cfbd = requests.get(url_cfbd, headers=headers, params=params_cfbd)
    
    games = res_cfbd.json() if res_cfbd.status_code == 200 else []
    
    # 2. Fetch Odds API lines
    url_odds = "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/"
    params_odds = {"api_key": ODDS_API_KEY, "regions": "us", "markets": "spreads", "oddsFormat": "american"}
    res_odds = requests.get(url_odds, params=params_odds)
    
    odds = res_odds.json() if res_odds.status_code == 200 else []
    
    # Package data cleanly for the website frontend
    payload = {
        "last_updated": str(datetime.utcnow()),
        "games_count": len(games),
        "games": games,
        "odds": odds
    }
    
    # Export to json file read by your website
    with open("games_output.json", "w") as f:
        import json
        json.dump(payload, f, indent=2)
        
    print("Successfully updated games_output.json!")

if __name__ == "__main__":
    main()
