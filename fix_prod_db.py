from kkoala import create_app
from kkoala.extensions import db
from sqlalchemy import text
import sys

# Create the app (using production config by default or whatever is set)
app = create_app("kkoala.config.ProdConfig")

# The actual head revision we want to force (found via 'flask db heads' locally)
TARGET_REVISION = "4b82cb051471"

with app.app_context():
    print(f"Attempting to FORCE reset database migration version to {TARGET_REVISION}...")
    try:
        # verify the table exists and check current version
        try:
            current_ver = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
            print(f"Current version in DB: {current_ver}")
        except Exception:
            print("alembic_version table likely does not exist. Skipping manual fix (init will handle it).")
            sys.exit(0)

        # Force the update using raw SQL to bypass Alembic's dependency checks
        print(f"Updating version to {TARGET_REVISION}...")
        db.session.execute(text("DELETE FROM alembic_version"))
        db.session.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{TARGET_REVISION}')"))
        db.session.commit()
        
        print(f"SUCCESS: Database version manually set to '{TARGET_REVISION}'.")
    except Exception as e:
        print(f"ERROR: Could not stamp database: {e}")
        db.session.rollback()
        sys.exit(1)

