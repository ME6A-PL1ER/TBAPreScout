class Event:
    def __init__(self, event_name, event_date, teams):
        self.event_name = event_name
        self.event_date = event_date
        self.teams = teams

    def __repr__(self):
        return f"Event(event_name={self.event_name}, event_date={self.event_date}, teams={self.teams})"