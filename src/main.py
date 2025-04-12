import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

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
    
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=10)
    
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
                team_name = team_info.get("nickname", f"Team {team_num}")
                
                events = frc_api.get_team_events(team_key, year)
                
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