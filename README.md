# FRC Team Event Tracker

A comprehensive tool for FIRST Robotics Competition (FRC) teams to track and analyze team performance across events, including alliance selections, rankings, awards, and match videos.

## Features

- Fetch team data from The Blue Alliance API
- View team rankings, alliance selections, and awards
- Search and filter team event data
- Export data to CSV or Excel
- Generate team performance summaries
- Watch and download match videos directly from the application

## Project Structure

```
frc-team-event-tracker
├── src
│   ├── api
│   │   ├── __init__.py
│   │   └── frc_api.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── event.py
│   │   └── team.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── formatters.py
│   ├── views
│   │   ├── __init__.py
│   │   └── display.py
│   └── main.py
├── config
│   └── config.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (optional, for better video download quality and format options)

### Basic Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/frc-team-event-tracker.git
   ```
2. Navigate to the project directory:
   ```
   cd frc-team-event-tracker
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

This will initialize the application, retrieve event data using the `FRCAPI`, and display the information in a structured format.