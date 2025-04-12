def display_event_data(event):
    print(f"Event Name: {event.event_name}")
    print(f"Event Date: {event.event_date}")
    print("Teams Participating:")
    for team in event.teams:
        picked_status = "Picked" if team.picked else "Not Picked"
        print(f"  - Team Number: {team.team_number}, Team Name: {team.team_name}, Status: {picked_status}")

def display_all_events(events):
    for event in events:
        display_event_data(event)
        print("\n")