import requests
import json
from datetime import datetime

CFBD_API_KEY = "BotEtAGH7nFzBkEwWJvCk8x6vT2gIEXfLBKvGgtC6IEv/2sa0ag79IMI6STxVpFK"
ODDS_API_KEY = "8a4959f73ddff1b6d07524bb82307d76"

CURRENT_YEAR = 2026
CURRENT_WEEK = 6  # Adjust to the current week

def main():
    print("Fetching live CFB lines and schedule...")
    
    # 1. Fetch live odds from The Odds API (always has active upcoming slate)
    url_odds = "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/"
    params_odds = {
        "api_key": ODDS_API_KEY,
        "regions": "us",
        "markets": "spreads",
        "oddsFormat": "american"
    }
    res_odds = requests.get(url_odds, params=params_odds)
    odds_data = res_odds.json() if res_odds.status_code == 200 else []

    # 2. Fetch games from CFBD
    headers_cfbd = {"Authorization": f"Bearer {CFBD_API_KEY}", "accept": "application/json"}
    url_cfbd = f"https://api.collegefootballdata.com/games?year={CURRENT_YEAR}&week={CURRENT_WEEK}&seasonType=regular"
    res_cfbd = requests.get(url_cfbd, headers=headers_cfbd)
    games_cfbd = res_cfbd.json() if res_cfbd.status_code == 200 else []

    # Fallback: If CFBD week query returns empty, build the slate directly from the active Odds API events
    final_games = []
    if games_cfbd:
        final_games = games_cfbd
    elif isinstance(odds_data, list) and len(odds_data) > 0:
        for item in odds_data:
            final_games.append({
                "home_team": item.get("home_team"),
                "away_team": item.get("away_team"),
                "start_date": item.get("commence_time")
            })

    payload = {
        "last_updated": str(datetime.utcnow()),
        "games_count": len(final_games),
        "games": final_games,
        "odds": odds_data
    }

    with open("games_output.json", "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Slate generated with {len(final_games)} matchups!")

if __name__ == "__main__":
    main()
