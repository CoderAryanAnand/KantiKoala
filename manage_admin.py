import argparse
from wsgi import application as app
from kkoala.extensions import db
from kkoala.models import User

def toggle_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found.")
            return

        user.is_admin = not user.is_admin
        # Also ensure they are a teacher if they are an admin? Not strictly required but helpful.
        # User requested "admin OR teacher" for lernen, so just admin is enough for access.
        
        db.session.commit()
        status = "Admin" if user.is_admin else "User"
        print(f"User '{username}' is now: {status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toggle admin status for a user.")
    parser.add_argument("username", help="The username of the user to update.")
    args = parser.parse_args()
    
    toggle_admin(args.username)
