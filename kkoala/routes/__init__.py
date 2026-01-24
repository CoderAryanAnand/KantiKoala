from .auth import auth_bp         # Authentication routes (login, register, etc.)
from .events import events_bp     # Agenda/Events API routes
from .grades import grades_bp     # Grades/Noten API routes
from .settings import settings_bp # User settings routes
from .todo import todo_bp         # ToDo list API routes
from .main import main_bp         # Main (public) routes
from .lernen import lernen_bp     # Learning/Theory routes
from .tools import tools_bp       # Tools routes (lerntimer, citation, etc.)
from .citations import citations_bp  # Citation generator API routes
from .admin import admin_bp       # Admin routes (user management)
from .notifications import notifications_bp # Notifications routes


def register_blueprints(app):
    """
    Register all Flask blueprints with their respective URL prefixes.

    Args:
        app (Flask): The Flask application instance.
    """
    app.register_blueprint(auth_bp, url_prefix="/auth")           # Auth routes under /auth
    app.register_blueprint(events_bp, url_prefix="/api/events")   # Events API under /api/events
    app.register_blueprint(grades_bp, url_prefix="/api/noten")    # Grades API under /api/noten
    app.register_blueprint(settings_bp, url_prefix="/settings")   # Settings under /settings
    app.register_blueprint(todo_bp, url_prefix="/api/todo")       # ToDo API under /api/todo
    app.register_blueprint(citations_bp, url_prefix="/api/citations")  # Citations API
    app.register_blueprint(lernen_bp, url_prefix="/lernen")       # Learning under /lernen
    app.register_blueprint(tools_bp, url_prefix="/tools")         # Tools under /tools
    app.register_blueprint(admin_bp, url_prefix="/admin")         # Admin under /admin
    app.register_blueprint(notifications_bp, url_prefix="/notifications") # Notifications routes
    app.register_blueprint(main_bp)                               # Main routes (no prefix)
