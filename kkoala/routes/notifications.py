from flask import Blueprint, request, jsonify, current_app, session
from kkoala.models import db, PushSubscription, User
from kkoala.utils import login_required
from pywebpush import webpush, WebPushException
import json
import os
from urllib.parse import urlparse

notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("/subscribe", methods=["POST"])
@login_required
def subscribe(user):
    data = request.get_json()
    if not data or "endpoint" not in data or "keys" not in data:
        return jsonify({"error": "Invalid subscription data"}), 400

    endpoint = data["endpoint"]
    keys = data["keys"]
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")
    
    # Check if subscription already exists
    # DEBUGGING FIX: Clear ALL old subscriptions for this user to prevent "410 Gone" errors from old endpoints.
    # This ensures we only have the freshest, working subscription.
    PushSubscription.query.filter_by(user_id=user.id).delete()
    
    new_sub = PushSubscription(
        user_id=user.id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth
    )
    db.session.add(new_sub)
    db.session.commit()

    return jsonify({"message": "Subscribed successfully"}), 201

def send_notification(title, description, user_id=None):
    """
    Sends a push notification to a specific user or all users.
    
    Args:
        title (str): The title of the notification.
        description (str): The body text of the notification.
        user_id (int, optional): The ID of the user to send to. If None, sends to all subscribed users.
    """
    
    # 1. Get subscriptions
    if user_id:
        subscriptions = PushSubscription.query.filter_by(user_id=user_id).all()
    else:
        subscriptions = PushSubscription.query.all()
        
    if not subscriptions:
        print("No subscriptions found.")
        return False

    # 2. Prepare payload
    notification_data = json.dumps({
        "title": title,
        "body": description
    })

    # 3. Get VAPID Private Key
    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
    
    # Handle case where Env Var contains the ACTUAL key content (PEM format)
    if vapid_private_key and "-----BEGIN PRIVATE KEY-----" in vapid_private_key:
        # Save it to a temporary file because pywebpush expects a file path or a PEM string?
        # Actually pywebpush's vapid_private_key arg can be a file path.
        # But 'webpush' function logic inside the library handles paths.
        # Let's write it to a temp file to be safe and compatible with current logic
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.pem') as temp:
                # DigitalOcean sometimes escapes newlines as \n string
                if "\\n" in vapid_private_key:
                    vapid_private_key = vapid_private_key.replace("\\n", "\n")
                temp.write(vapid_private_key)
                vapid_private_key = temp.name
        except Exception as e:
            print(f"Error creating temp key file: {e}")
            return False

    # Try to find the key file if env var is missing or assumes it's a path
    elif not vapid_private_key:
        possible_paths = [
            "private_key.pem",
            os.path.join(os.getcwd(), "private_key.pem")
        ]
        try:
            if current_app:
                possible_paths.insert(1, os.path.join(current_app.root_path, "..", "private_key.pem"))
        except RuntimeError:
            pass # No app context
             
        for path in possible_paths:
            if os.path.exists(path):
                vapid_private_key = os.path.abspath(path)
                break
    elif os.path.exists(vapid_private_key):
        vapid_private_key = os.path.abspath(vapid_private_key)

    if not vapid_private_key:
         print("Error: VAPID_PRIVATE_KEY not found.")
         return False

    vapid_claims = {
        "sub": "mailto:kantikoala@gmail.com"
    }

    # 4. Send notifications
    success_count = 0
    for sub in subscriptions:
        try:
            parsed_url = urlparse(sub.endpoint)
            audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            current_claims = vapid_claims.copy()
            current_claims["aud"] = audience

            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=notification_data,
                vapid_private_key=vapid_private_key,
                vapid_claims=current_claims
            )
            success_count += 1
        except WebPushException as ex:
            print(f"Web push failed for sub {sub.id}: {ex}")
            try:
                if ex.response and (ex.response.status_code == 410 or ex.response.status_code == 404):
                    db.session.delete(sub)
                    db.session.commit()
            except Exception:
                pass 
        except Exception as e:
            print(f"Unexpected error in webpush: {e}")

    print(f"Sent {success_count} notifications.")
    return True
