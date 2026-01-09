from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from ..models import User
from ..extensions import db
from ..utils import login_required

admin_bp = Blueprint("admin", __name__, template_folder="../templates")

@admin_bp.route("/users")
@login_required
def users(user):
    """
    List all users and allow role management.
    Restricted to admins.
    """
    if not user.is_admin:
        abort(403)
    
    query = request.args.get("q", "")
    if query:
        # Search by username or email
        users = User.query.filter(User.username.contains(query) | User.email.contains(query)).all()
    else:
        users = User.query.all()
        
    return render_template(
        "admin_users.html", 
        users=users, 
        current_user=user, 
        search_query=query
    )

@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_role(current_user, user_id):
    """
    Toggle admin or teacher role for a user.
    """
    if not current_user.is_admin:
        abort(403)
        
    user_to_edit = User.query.get_or_404(user_id)
    
    # Optional safety: prevent un-admining yourself to avoid lockout?
    # Unlikely to be asked for, but good practice. 
    # For now, simplistic implementation as requested.
    
    role = request.form.get("role")
    if role == "admin":
        user_to_edit.is_admin = not user_to_edit.is_admin
    elif role == "teacher":
        user_to_edit.is_teacher = not user_to_edit.is_teacher
        
    db.session.commit()
    flash(f"Berechtigungen für {user_to_edit.username} aktualisiert.", "success")
    return redirect(url_for("admin.users", q=request.form.get('q', '')))
