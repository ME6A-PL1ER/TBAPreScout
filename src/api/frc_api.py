import requests
import tbapy

class FRCAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.tba = tbapy.TBA(api_key)
    
    def get_team_data(self, team_key):
        """
        Retrieves information about a specific team.
        
        Args:
            team_key: The team key (e.g., 'frc254')
            
        Returns:
            dict: Team information
        """
        return self.tba.team(team_key)
    
    def get_team_events(self, team_key, year):
        """
        Retrieves all events a team participated in during a specific year.
        
        Args:
            team_key: The team key (e.g., 'frc254')
            year: The competition year
            
        Returns:
            list: List of events
        """
        return self.tba.team_events(team_key, year)
    
    def get_event_data(self, event_key):
        """
        Retrieves information about a specific event.
        
        Args:
            event_key: The event key (e.g., '2023carv')
            
        Returns:
            dict: Event information
        """
        return self.tba.event(event_key)
    
    def was_team_picked(self, team_key, event_key):
        """
        Determines if a team was picked for an alliance at a specific event.
        
        Args:
            team_key: The team key (e.g., 'frc254')
            event_key: The event key
            
        Returns:
            dict: Alliance information including:
                 - picked (bool): Whether the team was picked
                 - captain (bool): Whether the team was an alliance captain
                 - alliance (int): Alliance number (1-based)
                 - pick_number (int): Pick number within alliance
        """
        result = {
            "picked": False,
            "captain": False,
            "alliance": None,
            "pick_number": None
        }
        
        try:
            alliances = self.tba.event_alliances(event_key)
            
            if alliances is not None:
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
        except Exception as e:
            print(f"Error checking alliance status: {str(e)}")
        
        return result
    
    def fetch_awards(self, team_key, event_key):
        """Fetch awards won by a team at a specific event with recipient details"""
        try:
            url = f"https://www.thebluealliance.com/api/v3/team/{team_key}/event/{event_key}/awards"
            headers = {"X-TBA-Auth-Key": self.api_key}
            
            response = requests.get(url, headers=headers)
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
        """
        Get team rankings for an event
        
        Args:
            event_key: The event key
            
        Returns:
            dict: Team rankings information
        """
        try:
            return self.tba.event_rankings(event_key)
        except Exception as e:
            print(f"Error retrieving rankings for event {event_key}: {e}")
            return None