import sys
import os

# Ensure the script can see the kkoala package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kkoala import create_app
from kkoala.extensions import db
from kkoala.models import User

# Initialize the app with the default config (ProdConfig)
# You can change this by passing a different config string if needed
app = create_app()

def list_users():
    """Lists all users and their admin status."""
    with app.app_context():
        users = User.query.order_by(User.id).all()
        if not users:
            print("No users found in the database.")
            return []
        
        headers = f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin?'}"
        print(headers)
        print("-" * len(headers))
        
        for user in users:
            admin_status = "YES" if user.is_admin else "NO"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {admin_status}")
        
        return users

def toggle_admin(username):
    """Toggles the admin status of a user."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found.")
            return
        
        # Toggle status
        new_status = not user.is_admin
        user.is_admin = new_status
        
        try:
            db.session.commit()
            status_str = "ADMIN" if new_status else "USER"
            print(f"Success: '{username}' is now an {status_str}.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating database: {e}")

def main():
    """Main entry point for CLI or interactive mode."""
    
    # CLI Argument Mode
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            list_users()
        
        elif command == "toggle":
            if len(sys.argv) < 3:
                print("Usage: python manage_admin.py toggle <username>")
                return
            toggle_admin(sys.argv[2])
            
        elif command == "help":
             print("Usage:")
             print("  python manage_admin.py           (Interactive Mode)")
             print("  python manage_admin.py list      (List all users)")
             print("  python manage_admin.py toggle <username> (Toggle admin status)")
             
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for usage info.")
            
    # Interactive Mode (No arguments)
    else:
        print("\n=== KantiKoala Admin Manager ===\n")
        while True:
            users = list_users()
            if not users:
                break
                
            print("\nEnter username to toggle admin status (or press Enter to exit):")
            username = input("> ").strip()
            
            if not username:
                print("Exiting.")
                break
                
            toggle_admin(username)
            print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
