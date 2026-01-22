from datetime import time as dtime
from zoneinfo import ZoneInfo

DAY_START = dtime(8, 0)
FROM_EMAIL = "KantiKoala <noreply@kantikoala.app>"
DEFAULT_SETTINGS = {
    "learn_on_saturday": False,           # User learns on Saturdays (default: no)
    "learn_on_sunday": False,             # User learns on Sundays (default: no)
    "preferred_learning_time": "18:00",   # Preferred start time for learning blocks (as string)
    "study_block_color": "#0000FF",       # Default color for learning blocks (blue)
    "import_color": "#6C757D",            # Default color for imported events (Bootstrap secondary gray)
    "priority_settings": {                # Settings for different exam priorities
        1: {
            "color": "#770000",           # Color for priority 1 (dark red)
            "max_hours_per_day": 2.0,     # Max learning hours per day for priority 1
            "total_hours_to_learn": 14.0, # Total hours to schedule for priority 1
        },
        2: {
            "color": "#ca8300",           # Color for priority 2 (orange)
            "max_hours_per_day": 1.5,     # Max learning hours per day for priority 2
            "total_hours_to_learn": 7.0,  # Total hours to schedule for priority 2
        },
        3: {
            "color": "#097200",           # Color for priority 3 (green)
            "max_hours_per_day": 1.0,     # Max learning hours per day for priority 3
            "total_hours_to_learn": 4.0,  # Total hours to schedule for priority 3
        },
    },
    "time_zone": ZoneInfo("Europe/Zurich"),  # Default timezone for all users/events
}

DEFAULT_IMPORT_COLOR = "#6C757D"  # Bootstrap's secondary gray - neutral, professional, standard

# Templates available for users to import when creating a semester
SEMESTER_TEMPLATES = [
    {
        "id": 1,
        "name": "1. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Geschichte"]
    },
    {
        "id": 2,
        "name": "2. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 3,
        "name": "3. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 4,
        "name": "4. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Geografie", "Sport", "Englisch", "Französisch", "Informatik", "Wirtschaft und Recht", "Geschichte"]
    },
    {
        "id": 5,
        "name": "5. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Sport", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 6,
        "name": "6. Semester",
        "subjects": ["Deutsch", "Mathematik", "Biologie", "Chemie", "Sport", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 7,
        "name": "7. Semester",
        "subjects": ["Deutsch", "Mathematik", "Sport", "Physik", "Englisch", "Französisch", "Geschichte"]
    },
    {
        "id": 8,
        "name": "8. Semester",
        "subjects": ["Deutsch", "Mathematik", "Sport", "Physik", "Englisch", "Französisch", "Geschichte"]
    }
]

YEAR_SUBJECT_TEMPLATES = {
    1: SEMESTER_TEMPLATES[1]["subjects"],
    2: SEMESTER_TEMPLATES[3]["subjects"],
    3: SEMESTER_TEMPLATES[5]["subjects"],
    4: SEMESTER_TEMPLATES[7]["subjects"]
}

