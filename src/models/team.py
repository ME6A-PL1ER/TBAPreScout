class Team:
    def __init__(self, team_number, team_name, picked_for_alliance=False):
        self.team_number = team_number
        self.team_name = team_name
        self.picked_for_alliance = picked_for_alliance

    def __repr__(self):
        return f"Team({self.team_number}, '{self.team_name}', picked_for_alliance={self.picked_for_alliance})"

    def to_dict(self):
        return {
            "team_number": self.team_number,
            "team_name": self.team_name,
            "picked_for_alliance": self.picked_for_alliance
        }