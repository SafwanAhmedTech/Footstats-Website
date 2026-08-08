from flask import Flask, render_template, request, redirect
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import time

app = Flask(__name__)
load_dotenv()

CACHE = {}

LEAGUES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1"
}

API_KEY = os.getenv("API_KEY")
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")

@app.route("/")
def home():

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    # League table
    table_data = get_cached_data(

        key="PL_TABLE",

        url="https://api.football-data.org/v4/competitions/PL/standings",

        headers=headers,

        cache_time=600

    )

    leader = table_data["standings"][0]["table"][0]

    # Top scorers
    scorer_response = requests.get(
        "https://api.football-data.org/v4/competitions/PL/scorers",
        headers=headers
    )

    scorer_data = scorer_response.json()

    scorers = scorer_data.get("scorers", [])

    top_scorer = scorers[0] if scorers else None

    return render_template(
        "index.html",
        leader=leader,
        top_scorer=top_scorer
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/teams")
def teams():

    return render_template(
        "teams.html",
        leagues=LEAGUES
    )

@app.route("/teams/<league_code>")
def league_teams(league_code):

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    data = get_cached_data(

        key=f"LEAGUE_TEAMS_{league_code}",

        url=f"https://api.football-data.org/v4/competitions/{league_code}/teams",

        headers=headers,

        cache_time=86400

    )

    teams = data["teams"]

    return render_template(

        "league_teams.html",

        teams=teams,

        league=data["competition"]["name"]

    )

@app.route("/team/<int:team_id>")
def team(team_id):

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    # --------------------------------------------------
    # 1. Get team information
    # --------------------------------------------------

    club = get_cached_data(

        key=f"TEAM_{team_id}",

        url=f"https://api.football-data.org/v4/teams/{team_id}",

        headers=headers,

        cache_time=43200

    )

    if not club or "id" not in club:

        return render_template("404.html"), 404

    # Squad may not be available for every team
    squad = club.get("squad", [])


    # --------------------------------------------------
    # 2. Get upcoming fixtures
    # --------------------------------------------------

    fixture_data = get_cached_data(

        key=f"FIXTURES_{team_id}",

        url=f"https://api.football-data.org/v4/teams/{team_id}/matches",

        headers=headers,

        params={
            "status": "SCHEDULED",
            "limit": 3
        },

        cache_time=300

    )

    fixtures = fixture_data.get("matches", [])


    # --------------------------------------------------
    # 3. Get last 5 results
    # --------------------------------------------------

    result_data = get_cached_data(

        key=f"RESULTS_{team_id}",

        url=f"https://api.football-data.org/v4/teams/{team_id}/matches",

        headers=headers,

        params={
            "status": "FINISHED",
            "limit": 5
        },

        cache_time=300

    )

    results = result_data.get("matches", [])


    # --------------------------------------------------
    # 4. Calculate form
    # --------------------------------------------------

    form = []

    for match in results:

        home_goals = match["score"]["fullTime"]["home"]
        away_goals = match["score"]["fullTime"]["away"]

        if match["homeTeam"]["id"] == team_id:

            if home_goals > away_goals:
                form.append("W")

            elif home_goals < away_goals:
                form.append("L")

            else:
                form.append("D")

        else:

            if away_goals > home_goals:
                form.append("W")

            elif away_goals < home_goals:
                form.append("L")

            else:
                form.append("D")


    # --------------------------------------------------
    # 5. Find which league the team belongs to
    # --------------------------------------------------

    league_codes = {
        "PL": "Premier League",
        "PD": "La Liga",
        "BL1": "Bundesliga",
        "SA": "Serie A",
        "FL1": "Ligue 1"
    }

    team_league = None

    for league_code in league_codes:

        league_data = get_cached_data(

            key=f"LEAGUE_TEAMS_{league_code}",

            url=f"https://api.football-data.org/v4/competitions/{league_code}/teams",

            headers=headers,

            cache_time=86400

        )

        for league_team in league_data.get("teams", []):

            if league_team["id"] == team_id:

                team_league = league_code

                break

        if team_league:

            break


    # --------------------------------------------------
    # 6. Get the correct league table
    # --------------------------------------------------

    position = None

    if team_league:

        table_data = get_cached_data(

            key=f"{team_league}_TABLE",

            url=f"https://api.football-data.org/v4/competitions/{team_league}/standings",

            headers=headers,

            cache_time=600

        )

        standings = table_data.get("standings", [])

        if standings:

            table = standings[0].get("table", [])

            for row in table:

                if row["team"]["id"] == team_id:

                    position = row

                    break


    # --------------------------------------------------
    # 7. Render team page
    # --------------------------------------------------

    return render_template(

        "team.html",

        club=club,

        fixtures=fixtures,

        results=results,

        form=form,

        position=position,

        squad=squad

    )

@app.route("/table")
def table():

    url = "https://api.football-data.org/v4/competitions/PL/standings"

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    standings = data["standings"][0]["table"]

    return render_template(
        "table.html",
        standings=standings
    )

@app.route("/fixtures")
def fixtures():

    url = "https://api.football-data.org/v4/competitions/PL/matches"

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    data = get_cached_data(

        key="PL_FIXTURES",

        url="https://api.football-data.org/v4/competitions/PL/matches",

        headers=headers,

        cache_time=60

    )

    matches = data["matches"]

    live_matches = []
    fixtures = []

    for match in matches:

        if match["status"] in ["IN_PLAY", "PAUSED"]:

            live_matches.append(match)

        elif match["status"] in ["TIMED", "SCHEDULED"]:

            fixtures.append(match)

    for fixture in live_matches + fixtures:

        dt = datetime.fromisoformat(
            fixture["utcDate"].replace("Z", "+00:00")
        )

        uk_time = dt.astimezone(ZoneInfo("Europe/London"))

        fixture["formatted_date"] = uk_time.strftime("%d %B %Y")
        fixture["formatted_time"] = uk_time.strftime("%H:%M")

    return render_template(
        "fixtures.html",
        live_matches=live_matches,
        fixtures=fixtures
    )

@app.route("/results")
def results():

    url = "https://api.football-data.org/v4/competitions/PL/matches"

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    matches = data["matches"]

    return render_template(
        "results.html",
        matches=matches
    )

@app.route("/scorers")
def scorers():

    url = "https://api.football-data.org/v4/competitions/PL/scorers"

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    data = get_cached_data(

        key="PL_SCORERS",

        url="https://api.football-data.org/v4/competitions/PL/scorers",

        headers=headers,

        cache_time=1800

    )

    scorers = data["scorers"]

    return render_template(
        "scorers.html",
        scorers=scorers
    )


@app.route("/search")
def search():

    team_name = request.args.get("team", "").lower()

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    leagues = ["PL", "PD", "BL1", "SA", "FL1"]

    for league in leagues:

        data = get_cached_data(

            key=f"LEAGUE_TEAMS_{league}",

            url=f"https://api.football-data.org/v4/competitions/{league}/teams",

            headers=headers,

            cache_time=86400

        )

        for team in data["teams"]:

            if team_name in team["name"].lower():

                return redirect(f"/team/{team['id']}")

    return render_template("404.html"), 404

@app.route("/match/<int:match_id>")
def match(match_id):

    headers = {
        "X-Auth-Token": FOOTBALL_DATA_KEY
    }

    response = requests.get(
        "https://api.football-data.org/v4/competitions/PL/matches",
        headers=headers
    )

    data = response.json()

    matches = data["matches"]

    selected_match = None

    for fixture in matches:

        if fixture["id"] == match_id:
            selected_match = fixture
            break

    if selected_match is None:

        return render_template("404.html"), 404

    # Format the date and time
    if selected_match:

        dt = datetime.fromisoformat(
            selected_match["utcDate"].replace("Z", "+00:00")
        )

        selected_match["formatted_date"] = dt.strftime("%d %B %Y")

        selected_match["formatted_time"] = dt.strftime("%H:%M")

    return render_template(
        "match.html",
        match=selected_match
    )

def get_cached_data(key, url, headers, params=None, cache_time=300):

    current_time = time.time()

    if key in CACHE:

        data, timestamp = CACHE[key]

        if current_time - timestamp < cache_time:
            return data

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    CACHE[key] = (data, current_time)

    return data


@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):

    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)

