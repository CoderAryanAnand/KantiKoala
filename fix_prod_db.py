from kkoala import create_app
from flask_migrate import stamp
import sys

# Create the app (using production config by default or whatever is set)
app = create_app()

with app.app_context():
    print("Attempting to fix database migration version...")
    try:
        # This tells the database: "You are now at the latest version ('head')"
        # It ignores whatever ghost version (ff572563bb6e) the DB thinks it has.
        stamp() 
        print("SUCCESS: Database version stamped to 'head'.")
    except Exception as e:
        print(f"ERROR: Could not stamp database: {e}")
        sys.exit(1)
