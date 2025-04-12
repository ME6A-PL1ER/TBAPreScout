def format_event_data(event):
    formatted_event = {
        "Event Name": event.event_name,
        "Event Date": event.event_date,
        "Teams": []
    }
    for team in event.teams:
        formatted_event["Teams"].append(format_team_data(team))
    return formatted_event

def format_team_data(team):
    return {
        "Team Number": team.team_number,
        "Team Name": team.team_name,
        "Picked for Alliance": team.picked_for_alliance
    }