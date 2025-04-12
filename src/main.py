import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.frc_api import FRCAPI
from models.event import Event
from models.team import Team
from views.display import display_event_data, display_all_events
from config.config import API_KEY

def main():
    root = tk.Tk()
    root.title("FRC Team Event Tracker")
    root.geometry("900x600")
    
    frc_api = FRCAPI(API_KEY)
    
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
    input_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(input_frame, text="Team Numbers (comma-separated):").grid(row=0, column=0, padx=5, pady=5)
    team_entry = ttk.Entry(input_frame, width=30)
    team_entry.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(input_frame, text="Year:").grid(row=0, column=2, padx=5, pady=5)
    year_entry = ttk.Entry(input_frame, width=10)
    year_entry.insert(0, "2025")
    year_entry.grid(row=0, column=3, padx=5, pady=5)
    
    results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
    results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tree = ttk.Treeview(results_frame)
    tree['columns'] = ('Team Number', 'Team Name', 'Event Name', 'Event Date', 'Rank', 'Awards', 'Alliance Status')
    
    tree.column('#0', width=0, stretch=tk.NO)
    tree.column('Team Number', width=80, anchor=tk.CENTER)
    tree.column('Team Name', width=120, anchor=tk.W)
    tree.column('Event Name', width=180, anchor=tk.W)
    tree.column('Event Date', width=80, anchor=tk.CENTER)
    tree.column('Rank', width=50, anchor=tk.CENTER)
    tree.column('Awards', width=150, anchor=tk.W)
    tree.column('Alliance Status', width=120, anchor=tk.CENTER)
    
    tree.heading('#0', text='', anchor=tk.CENTER)
    tree.heading('Team Number', text='Team Number', anchor=tk.CENTER)
    tree.heading('Team Name', text='Team Name', anchor=tk.W)
    tree.heading('Event Name', text='Event Name', anchor=tk.W)
    tree.heading('Event Date', text='Event Date', anchor=tk.CENTER)
    tree.heading('Rank', text='Rank', anchor=tk.CENTER)
    tree.heading('Awards', text='Awards', anchor=tk.W)
    tree.heading('Alliance Status', text='Alliance Status', anchor=tk.CENTER)
    
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    summary_frame = ttk.LabelFrame(main_frame, text="Team Summary", padding="10")
    summary_frame.pack(fill=tk.X, pady=10)
    
    rank_alliance_summary_label = ttk.Label(summary_frame, text="Rank & Alliance Summary: ")
    rank_alliance_summary_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    rank_alliance_summary_value = ttk.Entry(summary_frame, font=("Arial", 10, "bold"), state="readonly", width=70)
    rank_alliance_summary_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    rank_alliance_summary_value.insert(0, "No data")
    
    awards_summary_label = ttk.Label(summary_frame, text="Awards Summary: ")
    awards_summary_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    awards_summary_value = ttk.Entry(summary_frame, font=("Arial", 10, "bold"), state="readonly", width=70)
    awards_summary_value.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    awards_summary_value.insert(0, "No data")
    
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    def clean_award_name(award_name):
        award_name = re.sub(r'\s+(sponsored|presented)\s+by.*', '', award_name, flags=re.IGNORECASE)
        
        award_name = re.sub(r'^FIRST\s+', '', award_name, flags=re.IGNORECASE)
        
        award_name = award_name.replace("District", "Dist.")
        
        award_name = award_name.replace("Championship", "Champ.")
        
        return award_name
    
    def generate_team_summary():
        if not tree.get_children():
            rank_alliance_summary_value.config(state="normal")
            rank_alliance_summary_value.delete(0, tk.END)
            rank_alliance_summary_value.insert(0, "No data")
            rank_alliance_summary_value.config(state="readonly")
            
            awards_summary_value.config(state="normal")
            awards_summary_value.delete(0, tk.END)
            awards_summary_value.insert(0, "No data")
            awards_summary_value.config(state="readonly")
            return
            
        team_data = {}
        for item in tree.get_children():
            values = tree.item(item)['values']
            team_num = values[0]
            if team_num not in team_data:
                team_data[team_num] = {
                    'name': values[1],
                    'events': []
                }
            
            rank = values[4]
            alliance_status = values[6]
            awards = values[5]
            
            if rank or alliance_status != "Unknown" or awards not in ["None", "Error"]:
                team_data[team_num]['events'].append({
                    'name': values[2],
                    'date': values[3],
                    'rank': rank,
                    'alliance_status': alliance_status,
                    'awards': awards
                })
        
        for team_num, data in team_data.items():
            ranks = [int(e['rank']) for e in data['events'] if e['rank']]
            total_ranked_events = len(ranks)
            
            if ranks:
                top_ranks = {}
                for r in sorted(ranks):
                    if r not in top_ranks:
                        top_ranks[r] = ranks.count(r)
                    if len(top_ranks) >= 3:
                        break
                
                rank_summary = " | ".join([f"{r}{'st' if r == 1 else 'nd' if r == 2 else 'rd' if r == 3 else 'th'} {count}/{total_ranked_events}" 
                                         for r, count in top_ranks.items()])
            else:
                rank_summary = "No ranking data"
                
            alliance_info = []
            for event in data['events']:
                if 'Alliance' in event.get('alliance_status', ''):
                    status = event['alliance_status']
                    if 'Captain' in status:
                        alliance_num = status.split('Alliance ')[1].split(' -')[0]
                        alliance_info.append(f"captain A{alliance_num}")
                    elif 'Pick' in status:
                        alliance_num = status.split('Alliance ')[1].split(' -')[0]
                        pick_num = status.split('Pick #')[1]
                        if pick_num == "1":
                            alliance_info.append(f"1st of A{alliance_num}")
                        else:
                            alliance_info.append(f"{pick_num}nd A{alliance_num}")
            
            alliance_summary = " | ".join(alliance_info) if alliance_info else "No alliance data"
            
            combined_summary = f"{rank_summary} | {alliance_summary}"
            if combined_summary == "No ranking data | No alliance data":
                combined_summary = "No data"
            
            all_awards = []
            for event in data['events']:
                if event.get('awards') and event['awards'] not in ["None", "Error"]:
                    all_awards.extend([a.strip() for a in event['awards'].split(";")])
            
            award_counts = {}
            for award in all_awards:
                cleaned_award = clean_award_name(award.split(" (")[0])
                award_counts[cleaned_award] = award_counts.get(cleaned_award, 0) + 1
            
            awards_summary = " | ".join([f"{award}{' x'+str(count) if count > 1 else ''}" 
                                       for award, count in award_counts.items()])
            
            if not awards_summary:
                awards_summary = "No awards data"
            
            rank_alliance_summary_value.config(state="normal")
            rank_alliance_summary_value.delete(0, tk.END)
            rank_alliance_summary_value.insert(0, combined_summary)
            rank_alliance_summary_value.config(state="readonly")
            
            awards_summary_value.config(state="normal")
            awards_summary_value.delete(0, tk.END)
            awards_summary_value.insert(0, awards_summary)
            awards_summary_value.config(state="readonly")
    
    def fetch_data():
        for item in tree.get_children():
            tree.delete(item)
        
        team_numbers = [num.strip() for num in team_entry.get().split(',') if num.strip()]
        if not team_numbers:
            messagebox.showerror("Error", "Please enter at least one team number")
            return
        
        try:
            year = int(year_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year")
            return
        
        progress = ttk.Progressbar(buttons_frame, mode="indeterminate")
        progress.pack(fill=tk.X, pady=5)
        progress.start()
        
        errors_encountered = []
        
        for team_num in team_numbers:
            team_key = f"frc{team_num}"
            try:
                team_info = frc_api.get_team_data(team_key)
                if not team_info:
                    raise ValueError(f"No data found for team {team_num}")
                    
                team_name = team_info.get("nickname", f"Team {team_num}")
                
                events = frc_api.get_team_events(team_key, year)
                if not events:
                    tree.insert('', tk.END, values=(team_num, team_name, "No events found", "", "", "", ""))
                    continue
                
                for event in events:
                    event_key = event.get("key")
                    event_name = event.get("name", "Unknown")
                    event_date = event.get("start_date", "Unknown")
                    
                    picked_status = "Unknown"
                    try:
                        alliance_info = frc_api.was_team_picked(team_key, event_key)
                        if alliance_info["picked"]:
                            alliance_text = f"Alliance {alliance_info['alliance']} - "
                            if alliance_info["captain"]:
                                picked_status = f"{alliance_text}Captain"
                            else:
                                picked_status = f"{alliance_text}Pick #{alliance_info['pick_number']}"
                        else:
                            picked_status = "Not Picked"
                    except Exception as e:
                        print(f"Error checking alliance status for team {team_num} at {event_key}: {e}")
                        picked_status = "Error"
                    
                    try:
                        awards_str = frc_api.fetch_awards(team_key, event_key)
                    except Exception as e:
                        print(f"Error fetching awards for team {team_num} at {event_key}: {e}")
                        awards_str = "Error"

                    rank = ''
                    try:
                        rankings = frc_api.get_event_rankings(event_key)
                        if rankings and 'rankings' in rankings:
                            for r in rankings['rankings']:
                                if r.get('team_key') == team_key:
                                    rank = r.get('rank', '')
                                    break
                    except Exception as e:
                        print(f"Error retrieving rankings for team {team_num} at event {event_key}: {e}")
                    
                    tree.insert('', tk.END, values=(team_num, team_name, event_name, event_date, rank, awards_str, picked_status))
                    
            except Exception as e:
                error_msg = f"Error fetching data for team {team_num}: {str(e)}"
                print(error_msg)
                errors_encountered.append(error_msg)
                continue
        
        progress.stop()
        progress.destroy()
        
        if errors_encountered:
            error_summary = "\n".join(errors_encountered[:5])
            if len(errors_encountered) > 5:
                error_summary += f"\n...and {len(errors_encountered) - 5} more errors"
            
            print(f"Encountered {len(errors_encountered)} errors while fetching data:")
            print(error_summary)
            
            messagebox.showinfo("Data Fetch Complete", 
                               f"Data retrieved with {len(errors_encountered)} errors.\n"
                               "See console for details.\n"
                               "The application will display all teams that were retrieved successfully.")
                               
        generate_team_summary()
    
    def export_data():
        if not tree.get_children():
            messagebox.showinfo("Export", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(','.join(tree['columns']) + '\n')
                
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    f.write(','.join([str(v).replace(',', ';') for v in values]) + '\n')
            
            messagebox.showinfo("Export", f"Data exported to {file_path}")
    
    ttk.Button(buttons_frame, text="Fetch Data", command=fetch_data).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Export to CSV", command=export_data).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()