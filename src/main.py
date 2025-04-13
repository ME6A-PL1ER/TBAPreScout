import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import re
import threading

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
    
    search_frame = ttk.Frame(results_frame, padding="5")
    search_frame.pack(fill=tk.X, pady=(0, 5))

    ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_in_var = tk.StringVar(value="all")
    ttk.Radiobutton(search_frame, text="All Fields", value="all", variable=search_in_var).pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(search_frame, text="Team Only", value="team", variable=search_in_var).pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(search_frame, text="Event Only", value="event", variable=search_in_var).pack(side=tk.LEFT, padx=5)

    def search_table():
        query = search_entry.get().strip().lower()
        search_type = search_in_var.get()
        
        if not query:
            for item in tree.get_children():
                tree.item(item, tags=())
            return
        
        for item in tree.get_children():
            values = tree.item(item)['values']
            match = False
            
            if search_type == "all":
                match = any(query in str(v).lower() for v in values)
            elif search_type == "team":
                match = (query in str(values[0]).lower() or 
                         query in str(values[1]).lower())
            elif search_type == "event":
                match = query in str(values[2]).lower()
                
            if match:
                tree.item(item, tags=("search_match",))
            else:
                tree.item(item, tags=())
                
        tree.tag_configure("search_match", background="#FFFF99")

    ttk.Button(search_frame, text="Search", command=search_table).pack(side=tk.LEFT, padx=5)
    ttk.Button(search_frame, text="Clear", command=lambda: [search_entry.delete(0, tk.END), search_table()]).pack(side=tk.LEFT, padx=5)

    search_entry.bind("<Return>", lambda e: search_table())
    
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
    
    def copy_to_clipboard(entry_widget):
        root.clipboard_clear()
        root.clipboard_append(entry_widget.get())
        root.update()
    
    rank_alliance_summary_label = ttk.Label(summary_frame, text="Rank & Alliance Summary: ")
    rank_alliance_summary_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    rank_alliance_summary_value = ttk.Entry(summary_frame, font=("Arial", 10, "bold"), state="readonly", width=70)
    rank_alliance_summary_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    rank_alliance_summary_value.insert(0, "No data")
    
    rank_alliance_copy_button = ttk.Button(summary_frame, text="Copy", command=lambda: copy_to_clipboard(rank_alliance_summary_value))
    rank_alliance_copy_button.grid(row=0, column=2, padx=5, pady=5)
    
    awards_summary_label = ttk.Label(summary_frame, text="Awards Summary: ")
    awards_summary_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    
    awards_summary_value = ttk.Entry(summary_frame, font=("Arial", 10, "bold"), state="readonly", width=70)
    awards_summary_value.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    awards_summary_value.insert(0, "No data")
    
    awards_copy_button = ttk.Button(summary_frame, text="Copy", command=lambda: copy_to_clipboard(awards_summary_value))
    awards_copy_button.grid(row=1, column=2, padx=5, pady=5)
    
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    def clean_award_name(award_name):
        award_name = re.sub(r'\s+(sponsored|presented)\s+by.*', '', award_name, flags=re.IGNORECASE)
        
        award_name = re.sub(r'\s+in honor of Jack Kamen.*', '', award_name, flags=re.IGNORECASE)
        
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
                rank_summary_parts = []
                
                first_places = ranks.count(1)
                if first_places > 0:
                    rank_summary_parts.append(f"1st {first_places}/{total_ranked_events}")
                
                top3_count = sum(1 for r in ranks if 1 < r <= 3)
                if top3_count > 0:
                    rank_summary_parts.append(f"top 3 {top3_count}/{total_ranked_events}")
                
                top5_count = sum(1 for r in ranks if 3 < r <= 5)
                if top5_count > 0:
                    rank_summary_parts.append(f"top 5 {top5_count}/{total_ranked_events}")
                
                top10_count = sum(1 for r in ranks if 5 < r <= 10)
                if top10_count > 0:
                    rank_summary_parts.append(f"top 10 {top10_count}/{total_ranked_events}")
                
                if rank_summary_parts:
                    rank_summary = " | ".join(rank_summary_parts)
                else:
                    rank_summary = "No notable rankings"
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
                            alliance_info.append(f"1st A{alliance_num}")
                        elif pick_num == "2":
                            alliance_info.append(f"2nd A{alliance_num}")
                        elif pick_num == "3":
                            alliance_info.append(f"3rd/backup A{alliance_num}")
            
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
            
        export_window = tk.Toplevel(root)
        export_window.title("Export Options")
        export_window.geometry("400x350")
        export_window.transient(root)
        export_window.grab_set()
        
        ttk.Label(export_window, text="Select export options:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        export_fields = {}
        for field in tree['columns']:
            export_fields[field] = tk.BooleanVar(value=True)
            ttk.Checkbutton(export_window, text=field, variable=export_fields[field]).pack(anchor=tk.W, padx=20)
        
        export_format_var = tk.StringVar(value="csv")
        format_frame = ttk.LabelFrame(export_window, text="Export Format")
        format_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Radiobutton(format_frame, text="CSV", value="csv", variable=export_format_var).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(format_frame, text="Excel", value="excel", variable=export_format_var).pack(side=tk.LEFT, padx=15)
        
        filter_frame = ttk.LabelFrame(export_window, text="Export Filter")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All Rows", value="all", variable=filter_var).pack(anchor=tk.W, padx=15)
        ttk.Radiobutton(filter_frame, text="Selected Rows Only", value="selected", variable=filter_var).pack(anchor=tk.W, padx=15)
        ttk.Radiobutton(filter_frame, text="Search Results Only", value="search", variable=filter_var).pack(anchor=tk.W, padx=15)
        
        def do_export():
            selected_fields = [field for field, var in export_fields.items() if var.get()]
            if not selected_fields:
                messagebox.showinfo("Export", "Please select at least one field to export")
                return
                
            export_format = export_format_var.get()
            filter_type = filter_var.get()
            
            rows_to_export = []
            if filter_type == "all":
                items = tree.get_children()
            elif filter_type == "selected":
                items = tree.selection()
                if not items:
                    messagebox.showinfo("Export", "No rows selected")
                    return
            elif filter_type == "search":
                items = [item for item in tree.get_children() if "search_match" in tree.item(item, "tags")]
                if not items:
                    messagebox.showinfo("Export", "No search results found")
                    return
            
            for item in items:
                values = tree.item(item)['values']
                row_data = {field: values[tree['columns'].index(field)] for field in selected_fields}
                rows_to_export.append(row_data)
            
            if export_format == "csv":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                    
                with open(file_path, 'w') as f:
                    f.write(','.join(selected_fields) + '\n')
                    
                    for row in rows_to_export:
                        f.write(','.join([str(row.get(field, '')).replace(',', ';') for field in selected_fields]) + '\n')
                
                messagebox.showinfo("Export", f"Data exported to {file_path}")
                export_window.destroy()
                
            elif export_format == "excel":
                try:
                    import pandas as pd
                except ImportError:
                    result = messagebox.askyesno(
                        "Missing Package", 
                        "pandas and openpyxl packages are required to export to Excel. Would you like to install them now?"
                    )
                    if result:
                        import subprocess
                        import sys
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
                        import pandas as pd
                    else:
                        return
                
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                )
                if not file_path:
                    return
                    
                df = pd.DataFrame(rows_to_export)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Export", f"Data exported to {file_path}")
                export_window.destroy()
        
        button_frame = ttk.Frame(export_window)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Export", command=do_export).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=export_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def show_videos():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showinfo("Videos", "Please select a team event first")
            return
            
        values = tree.item(selected_item)['values']
        team_num = values[0]
        event_name = values[2]
        
        team_key = f"frc{team_num}"
        year = int(year_entry.get())
        
        events = frc_api.get_team_events(team_key, year)
        event_key = None
        for event in events:
            if event.get("name") == event_name:
                event_key = event.get("key")
                break
        
        if not event_key:
            messagebox.showinfo("Videos", f"Could not find event key for {event_name}")
            return
        
        loading_window = tk.Toplevel(root)
        loading_window.title("Loading Videos")
        loading_window.geometry("300x100")
        loading_window.transient(root)
        loading_window.grab_set()
        
        ttk.Label(loading_window, text=f"Fetching videos for team {team_num}...", 
                  font=("Arial", 10)).pack(pady=(20, 5))
        progress = ttk.Progressbar(loading_window, mode="indeterminate", length=250)
        progress.pack(pady=5)
        progress.start()
        
        def fetch_videos_thread():
            videos = frc_api.get_team_event_videos(team_key, event_key)
            
            loading_window.after(0, lambda: loading_window.destroy())
            
            if not videos:
                root.after(0, lambda: messagebox.showinfo("Videos", f"No videos found for team {team_num} at {event_name}"))
                return
            
            root.after(0, lambda: display_videos(videos, team_num, event_name))
        
        thread = threading.Thread(target=fetch_videos_thread)
        thread.daemon = True
        thread.start()

    def display_videos(videos, team_num, event_name):
        video_window = tk.Toplevel(root)
        video_window.title(f"Videos for Team {team_num} at {event_name}")
        video_window.geometry("800x500")
        
        videos_frame = ttk.Frame(video_window, padding="10")
        videos_frame.pack(fill=tk.BOTH, expand=True)
        
        category_frame = ttk.Frame(videos_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        category_var = tk.StringVar(value="all")
        ttk.Radiobutton(category_frame, text="All Videos", value="all", 
                        variable=category_var, command=lambda: filter_videos(category_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(category_frame, text="Matches Only", value="match", 
                        variable=category_var, command=lambda: filter_videos(category_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(category_frame, text="Team Media", value="team", 
                        variable=category_var, command=lambda: filter_videos(category_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(category_frame, text="Event Media", value="event", 
                        variable=category_var, command=lambda: filter_videos(category_var.get())).pack(side=tk.LEFT, padx=5)
        
        search_frame = ttk.Frame(videos_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: filter_videos(category_var.get()))
        
        ttk.Button(search_frame, text="Clear", command=lambda: [search_entry.delete(0, tk.END), 
                                                              filter_videos(category_var.get())]).pack(side=tk.LEFT, padx=5)
        
        video_tree = ttk.Treeview(videos_frame)
        video_tree['columns'] = ('Title', 'Type', 'Source')
        
        video_tree.column('#0', width=0, stretch=tk.NO)
        video_tree.column('Title', width=500, anchor=tk.W)
        video_tree.column('Type', width=100, anchor=tk.CENTER)
        video_tree.column('Source', width=100, anchor=tk.CENTER)
        
        video_tree.heading('#0', text='', anchor=tk.CENTER)
        video_tree.heading('Title', text='Title', anchor=tk.W)
        video_tree.heading('Type', text='Type', anchor=tk.CENTER)
        video_tree.heading('Source', text='Source', anchor=tk.CENTER)
        
        video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(videos_frame, orient="vertical", command=video_tree.yview)
        video_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        match_videos = []
        other_videos = []
        
        for video in videos:
            title = video.get('title', 'Untitled')
            video_type = video.get('type', 'youtube').replace('youtube_', '')
            source = video.get('source', 'unknown')
            url = video.get('url', '')
            
            item_data = {
                'title': title,
                'type': video_type,
                'source': source,
                'url': url
            }
            
            if source == 'match':
                match_type = None
                match_num = None
                
                if "Qualification Match" in title:
                    match_type = "qm"
                    match_num = int(title.split("Qualification Match ")[1])
                elif "Quarter Final" in title:
                    match_type = "qf"
                    match_num = int(title.split("Quarter Final ")[1])
                elif "Semi Final" in title:
                    match_type = "sf"
                    match_num = int(title.split("Semi Final ")[1])
                elif "Final" in title and not "Quarter" in title and not "Semi" in title:
                    match_type = "f"
                    match_num = int(title.split("Final ")[1])
                elif "Eighth Final" in title:
                    match_type = "ef"
                    match_num = int(title.split("Eighth Final ")[1])
                else:
                    match_parts = title.split("Match ")
                    if len(match_parts) > 1:
                        try:
                            match_num = int(match_parts[1])
                            match_type = "other"
                        except ValueError:
                            match_num = 9999
                            match_type = "unknown"
                    else:
                        match_num = 9999
                        match_type = "unknown"
                    
                match_videos.append((match_type, match_num, item_data))
            else:
                other_videos.append(item_data)
        
        match_type_order = {'qm': 0, 'ef': 1, 'qf': 2, 'sf': 3, 'f': 4, 'other': 5, 'unknown': 6}
        match_videos.sort(key=lambda x: (match_type_order.get(x[0], 99), x[1]))
        
        all_items = []
        
        for match_type, match_num, item_data in match_videos:
            item = video_tree.insert('', tk.END, values=(
                item_data['title'],
                item_data['type'],
                item_data['source']
            ), tags=('match',))
            all_items.append((item, item_data))
        
        for item_data in other_videos:
            item = video_tree.insert('', tk.END, values=(
                item_data['title'],
                item_data['type'],
                item_data['source']
            ), tags=(item_data['source'],))
            all_items.append((item, item_data))
        
        video_tree.tag_configure('match', background='#E8F4F0')
        video_tree.tag_configure('team', background='#F4F0E8')
        video_tree.tag_configure('event', background='#F0E8F4')
        
        def filter_videos(category):
            search_text = search_entry.get().lower()
            
            for item in video_tree.get_children():
                video_tree.delete(item)
            
            for item_id, item_data in all_items:
                source = item_data['source']
                title = item_data['title'].lower()
                
                if category != 'all' and source != category:
                    continue
                    
                if search_text and search_text not in title:
                    continue
                    
                video_tree.insert('', tk.END, values=(
                    item_data['title'],
                    item_data['type'],
                    item_data['source']
                ), tags=(source,))
        
        buttons_frame = ttk.Frame(video_window)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def open_video():
            selected = video_tree.focus()
            if not selected:
                messagebox.showinfo("Open Video", "Please select a video first")
                return
                
            selected_title = video_tree.item(selected)['values'][0]
            selected_source = video_tree.item(selected)['values'][2]
            
            video_url = None
            for _, item_data in all_items:
                if item_data['title'] == selected_title and item_data['source'] == selected_source:
                    video_url = item_data['url']
                    break
                    
            if video_url:
                import webbrowser
                webbrowser.open(video_url)
            else:
                messagebox.showinfo("Open Video", "Couldn't find URL for selected video")
        
        ttk.Button(buttons_frame, text="Open in Browser", command=open_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Download", command=lambda: download_video(False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Download All Videos", command=lambda: download_video(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", command=video_window.destroy).pack(side=tk.RIGHT, padx=5)

        def download_video(is_playlist=False):
            try:
                import yt_dlp
            except ImportError:
                result = messagebox.askyesno(
                    "Missing Package", 
                    "yt-dlp package is required to download videos but is not installed. Would you like to install it now?"
                )
                if result:
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                    messagebox.showinfo("Success", "yt-dlp installed successfully")
                    import yt_dlp
                else:
                    return
                    
            import shutil
            has_ffmpeg = shutil.which('ffmpeg') is not None

            if not is_playlist:
                selected = video_tree.focus()
                if not selected:
                    messagebox.showinfo("Download Video", "Please select a video first")
                    return
                
                selected_title = video_tree.item(selected)['values'][0]
                selected_source = video_tree.item(selected)['values'][2]
                
                video_url = None
                video_type = None
                for _, item_data in all_items:
                    if item_data['title'] == selected_title and item_data['source'] == selected_source:
                        video_url = item_data['url']
                        video_type = item_data['type']
                        break
                        
                if not video_url or video_url == "https://www.youtube.com/watch?v=":
                    messagebox.showerror("Error", "Invalid video URL. The video ID is missing.")
                    return
            else:
                if not video_tree.get_children():
                    messagebox.showinfo("Download Videos", "No videos to download")
                    return
                
                video_urls = []
                for item in video_tree.get_children():
                    selected_title = video_tree.item(item)['values'][0]
                    selected_source = video_tree.item(item)['values'][2]
                    
                    for _, item_data in all_items:
                        if item_data['title'] == selected_title and item_data['source'] == selected_source:
                            url = item_data['url']
                            if url and url != "https://www.youtube.com/watch?v=":
                                video_urls.append(url)
                            break
                        
                if not video_urls:
                    messagebox.showerror("Error", "No valid video URLs found")
                    return
                    
                video_type = "multiple"

            options_window = tk.Toplevel(video_window)
            options_window.title("Download Options")
            options_window.geometry("400x300")
            options_window.transient(video_window)
            options_window.grab_set()
            
            quality_frame = ttk.LabelFrame(options_window, text="Select Quality")
            quality_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)
            
            quality_var = tk.StringVar(value="best")
            
            quality_canvas = tk.Canvas(quality_frame)
            scrollbar = ttk.Scrollbar(quality_frame, orient="vertical", command=quality_canvas.yview)
            scrollable_frame = ttk.Frame(quality_canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: quality_canvas.configure(
                    scrollregion=quality_canvas.bbox("all")
                )
            )
            
            quality_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            quality_canvas.configure(yscrollcommand=scrollbar.set)
            
            quality_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            loading_label = ttk.Label(options_window, text="Fetching available formats...", font=("Arial", 9, "italic"))
            loading_label.pack(pady=5)
            
            progress = ttk.Progressbar(options_window, mode="indeterminate")
            progress.pack(fill=tk.X, padx=10, expand=True)
            progress.start()
            
            def update_quality_options(formats):
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()
                    
                ttk.Radiobutton(
                    scrollable_frame, 
                    text="Best available quality", 
                    value="best", 
                    variable=quality_var
                ).pack(anchor=tk.W, padx=10, pady=2)
                
                ttk.Radiobutton(
                    scrollable_frame, 
                    text="Audio only", 
                    value="bestaudio/best", 
                    variable=quality_var
                ).pack(anchor=tk.W, padx=10, pady=2)
                
                seen_heights = set()
                
                for format_info in formats:
                    if 'height' in format_info and format_info['height'] is not None:
                        height = format_info['height']
                        
                        if height not in seen_heights:
                            seen_heights.add(height)
                            format_note = format_info.get('format_note', f"{height}p")
                            
                            ttk.Radiobutton(
                                scrollable_frame, 
                                text=f"{height}p ({format_note})", 
                                value=f"bestvideo[height<={height}]+bestaudio/best[height<={height}]", 
                                variable=quality_var
                            ).pack(anchor=tk.W, padx=10, pady=2)
            
            def select_save_path():
                progress.stop()
                
                if video_type.lower() == "playlist" or is_playlist:
                    dir_path = filedialog.askdirectory(title="Select folder to save video(s)")
                    if not dir_path:
                        return False
                    
                    output_path = dir_path
                    is_dir = True
                else:
                    file_path = filedialog.asksaveasfilename(
                        title="Save video as",
                        defaultextension=".mp4",
                        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
                    )
                    if not file_path:
                        return False
                    
                    output_path = file_path
                    is_dir = False
                
                options_window.destroy()
                
                progress_window = tk.Toplevel(video_window)
                progress_window.title("Downloading Video(s)")
                progress_window.geometry("400x150")
                progress_window.transient(video_window)
                progress_window.grab_set()
                
                progress_label = ttk.Label(progress_window, text="Preparing download...")
                progress_label.pack(pady=(10, 5))
                
                progress_bar = ttk.Progressbar(progress_window, mode="indeterminate", length=300)
                progress_bar.pack(pady=5)
                progress_bar.start()
                
                status_label = ttk.Label(progress_window, text="")
                status_label.pack(pady=5)
                
                cancel_button = ttk.Button(progress_window, text="Cancel", command=progress_window.destroy)
                cancel_button.pack(pady=10)
                
                def download_thread():
                    try:
                        ydl_opts = {
                            'format': quality_var.get() if has_ffmpeg else quality_var.get().replace('+', '/'),
                            'progress_hooks': [
                                lambda d: update_progress(d, status_label)
                            ],
                            'postprocessors': [],
                            'nopart': True,
                            'quiet': False,
                            'no_warnings': False
                        }
                        
                        if not has_ffmpeg:
                            ydl_opts['format_sort'] = ['res', 'ext']
                            ydl_opts['merge_output_format'] = None
                        
                        if is_dir:
                            ydl_opts['outtmpl'] = f"{output_path}/%(title)s.%(ext)s"
                        else:
                            ydl_opts['outtmpl'] = output_path
                        
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            if is_playlist:
                                ydl.download(video_urls)
                            else:
                                ydl.download([video_url])
                        
                        progress_window.after(0, lambda: complete_download(progress_window, "Download complete!"))
                        
                    except Exception as err:
                        progress_window.after(0, lambda: complete_download(progress_window, f"Error: {str(err)}"))
                
                def update_progress(d, label):
                    if d['status'] == 'downloading':
                        if '_percent_str' in d:
                            progress_window.after(0, lambda: label.config(text=f"Downloading: {d['_percent_str']} at {d.get('_speed_str', 'N/A')}"))
                    elif d['status'] == 'finished':
                        progress_window.after(0, lambda: label.config(text="Download finished, processing..."))
                
                def complete_download(window, message):
                    progress_bar.stop()
                    status_label.config(text=message)
                    cancel_button.config(text="Close")
                
                download_thread = threading.Thread(target=download_thread)
                download_thread.daemon = True
                download_thread.start()
                
                return True
            
            def fetch_formats_thread():
                try:
                    with yt_dlp.YoutubeDL() as ydl:
                        if is_playlist:
                            if video_urls:
                                info = ydl.extract_info(video_urls[0], download=False)
                            else:
                                info = {}
                        else:
                            info = ydl.extract_info(video_url, download=False)
                            
                        formats = info.get('formats', [])
                        options_window.after(0, lambda: update_quality_options(formats))
                        options_window.after(0, lambda: loading_label.config(text="Select quality settings:"))
                        options_window.after(0, progress.stop)
                        options_window.after(0, progress.pack_forget)
                except Exception as err:
                    basic_formats = []
                    quality_heights = [2160, 1440, 1080, 720, 480, 360, 240]
                    for height in quality_heights:
                        basic_formats.append({'height': height, 'format_note': f'{height}p'})
                        
                    options_window.after(0, lambda: update_quality_options(basic_formats))
                    options_window.after(0, lambda: loading_label.config(text="Available formats could not be retrieved. Using default options:"))
                    options_window.after(0, progress.stop)
                    options_window.after(0, progress.pack_forget)
            
            formats_thread = threading.Thread(target=fetch_formats_thread)
            formats_thread.daemon = True
            formats_thread.start()
            
            ttk.Button(
                options_window, 
                text="Download", 
                command=select_save_path
            ).pack(pady=10)
    
    ttk.Button(buttons_frame, text="Fetch Data", command=fetch_data).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Export to CSV", command=export_data).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Show Videos", command=show_videos).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()