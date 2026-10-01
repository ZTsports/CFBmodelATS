import requests
import json
import re
from datetime import datetime, timezone

CFBD_API_KEY = "BotEtAGH7nFzBkEwWJvCk8x6vT2gIEXfLBKvGgtC6IEv/2sa0ag79IMI6STxVpFK"
ODDS_API_KEY = "8a4959f73ddff1b6d07524bb82307d76"

CURRENT_YEAR = 2026
CURRENT_WEEK = 6

# Common name aliases between CFBD and Odds API
NAME_MAP = {
    "fiu": "florida international",
    "florida international panthers": "florida international",
    "utsa": "utsa",
    "utsa roadrunners": "utsa",
    "southern miss": "southern miss",
    "southern mississipi": "southern miss",
    "southern mississippi golden eagles": "southern miss",
    "usf": "south florida",
    "south florida bulls": "south florida",
    "troy trojans": "troy",
    "kennesaw state owls": "kennesaw state",
    "jacksonville state gamecocks": "jacksonville state",
    "sam houston bearkats": "sam houston",
    "sam houston state": "sam houston",
    "liberty flames": "liberty",
    "arkansas state red wolves": "arkansas state",
    "south alabama jaguars": "south alabama",
    "western kentucky hilltoppers": "western kentucky",
    "wku": "western kentucky",
    "missouri state bears": "missouri state"
}

def clean_team_name(name):
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    # Check alias map
    if name in NAME_MAP:
        return NAME_MAP[name]
    # Return core words
    return name

def extract_draftkings_spread(odds_item, home_team):
    """Finds DraftKings spread for the home team."""
    if not odds_item or "bookmakers" not in odds_item:
        return None
    
    # Prioritize DraftKings, fallback to first available US bookmaker
    bookmaker = next((b for b in odds_item["bookmakers"] if b.get("key") == "draftkings"), None)
    if not bookmaker and odds_item["bookmakers"]:
        bookmaker = odds_item["bookmakers"][0]
        
    if not bookmaker or "markets" not in bookmaker:
        return None
        
    spread_market = next((m for m in bookmaker["markets"] if m.get("key") == "spreads"), None)
    if not spread_market or "outcomes" not in spread_market:
        return None
        
    # Match the home outcome
    cleaned_home = clean_team_name(home_team)
    for outcome in spread_market["outcomes"]:
        outcome_name = clean_team_name(outcome.get("name", ""))
        # If words overlap significantly
        if cleaned_home in outcome_name or outcome_name in cleaned_home:
            point = outcome.get("point")
            if point is not None:
                sign = "+" if point > 0 else ""
                return f"{home_team} {sign}{point}"
                
    # If home outcome not found, return the first one available formatted
    first_out = spread_market["outcomes"][0]
    p = first_out.get("point")
    s = "+" if p and p > 0 else ""
    return f"{first_out.get('name')} {s}{p}" if p is not None else None

def main():
    print(f"Fetching Week {CURRENT_WEEK} slate and DraftKings odds...")
    
    # 1. Fetch live odds
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

    # Choose dataset
    slate = games_cfbd if games_cfbd else odds_data
    
    processed_games = []
    for g in slate:
        home = g.get("home_team") or g.get("homeTeam") or ""
        away = g.get("away_team") or g.get("awayTeam") or ""
        start_date = g.get("start_date") or g.get("commence_time") or ""

        # Find matching game in odds_data
        matched_line = "Line Pending"
        clean_home = clean_team_name(home)
        
        if isinstance(odds_data, list):
            for odds_item in odds_data:
                odds_home = clean_team_name(odds_item.get("home_team", ""))
                # Flexible match: either identical, contains, or mapped
                if (clean_home and odds_home) and (clean_home in odds_home or odds_home in clean_home):
                    spread = extract_draftkings_spread(odds_item, home)
                    if spread:
                        matched_line = spread
                        break

        processed_games.append({
            "home_team": home,
            "away_team": away,
            "start_date": start_date,
            "draftkings_line": matched_line
        })

    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "games_count": len(processed_games),
        "games": processed_games
    }

    with open("games_output.json", "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Slate ready! Processed {len(processed_games)} games.")

if __name__ == "__main__":
    main()
