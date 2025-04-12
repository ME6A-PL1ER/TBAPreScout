import requests

class FRCAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.thebluealliance.com/api/v3"
        self.headers = {"X-TBA-Auth-Key": api_key}

    def get_team_data(self, team_key):
        url = f"{self.base_url}/team/{team_key}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_team_events(self, team_key, year):
        url = f"{self.base_url}/team/{team_key}/events/{year}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_event_data(self, event_key):
        url = f"{self.base_url}/event/{event_key}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def was_team_picked(self, team_key, event_key):
        result = {
            "picked": False,
            "captain": False,
            "alliance": None,
            "pick_number": None
        }

        try:
            url = f"{self.base_url}/event/{event_key}/alliances"
            response = requests.get(url, headers=self.headers)
            alliances = response.json() if response.status_code == 200 else []

            if alliances:
                for i, alliance in enumerate(alliances):
                    if isinstance(alliance, dict):
                        picks = alliance.get('picks', [])
                        if team_key in picks:
                            result["picked"] = True
                            result["alliance"] = i + 1
                            pick_index = picks.index(team_key)
                            result["pick_number"] = pick_index + 1
                            result["captain"] = (pick_index == 0)
                            break

            return result
        except Exception as e:
            print(f"Error determining if team {team_key} was picked: {e}")
            return result

    def fetch_awards(self, team_key, event_key):
        try:
            url = f"{self.base_url}/team/{team_key}/event/{event_key}/awards"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"API call failed with status code: {response.status_code}")
                return "Error"

            awards = response.json()
            if not awards:
                return "None"

            award_strings = []
            for award in awards:
                award_name = award.get('name', 'Unknown Award')

                recipients = award.get('recipient_list', [])
                for recipient in recipients:
                    if recipient.get('team_key') == team_key and recipient.get('awardee'):
                        award_name += f" ({recipient['awardee']})"
                        break

                award_strings.append(award_name)

            result = "; ".join(award_strings)
            return result if result else "None"
        except Exception as e:
            print(f"Error fetching awards: {e}")
            return "Error"

    def get_event_rankings(self, event_key):
        try:
            url = f"{self.base_url}/event/{event_key}/rankings"
            response = requests.get(url, headers=self.headers)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error retrieving rankings for event {event_key}: {e}")
            return None

    def get_team_ranking(self, team_key, event_key):
        try:
            rankings_data = self.get_event_rankings(event_key)

            if not rankings_data or 'rankings' not in rankings_data:
                print(f"No ranking data available for event {event_key}")
                return None

            for team_ranking in rankings_data['rankings']:
                if team_ranking.get('team_key') == team_key:
                    return team_ranking

            print(f"Team {team_key} not found in rankings for event {event_key}")
            return None
        except Exception as e:
            print(f"Error getting ranking for team {team_key} at event {event_key}: {e}")
            return None

    def display_team_data(self, team_key, event_key):
        team_data = self.get_team_data(team_key)
        if team_data is None:
            print(f"Could not retrieve data for team {team_key}")
            return

        team_name = team_data.get('nickname', 'Unknown')

        ranking = self.get_team_ranking(team_key, event_key)
        if ranking:
            rank = ranking.get('rank', 'N/A')
            print(f"Team {team_name} is ranked {rank} at {event_key}")
        else:
            print(f"No ranking information found for Team {team_name} at {event_key}")