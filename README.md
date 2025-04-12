# FRC Team Event Tracker

This project is designed to retrieve and display event data for FRC (FIRST Robotics Competition) teams, including information on whether teams were picked for alliances.

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