# Import Flask extensions for database, password hashing, and migrations
from flask_sqlalchemy import SQLAlchemy      # ORM for database models and queries
from flask_bcrypt import Bcrypt              # Secure password hashing
from flask_migrate import Migrate            # Database schema migrations
from flask_limiter import Limiter            # Rate limiting for endpoints
from flask_limiter.util import get_remote_address  # Get client IP for rate limiting

# Instantiate the extensions (to be initialized with the Flask app in the factory)
db = SQLAlchemy()    # Handles all database operations and models
bcrypt = Bcrypt()    # Provides methods for hashing and checking passwords
migrate = Migrate()  # Manages database migrations (schema changes)
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
