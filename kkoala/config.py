"""
Configuration module for the Flask application.

This module defines different configuration classes for various environments:
- BaseConfig: Common settings shared across all environments.
- ProdConfig: Settings specific to the production environment (Heroku/Render).
- DevConfig: Settings for local development with SQLite.
- TestConfig: Settings for running tests in an in-memory database.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """
    Base configuration class containing common settings.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESEND_API_KEY = os.getenv("RESEND_API_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # Keep CREATE_DB False in production
    CREATE_DB = False


class ProdConfig(BaseConfig):
    """
    Production configuration class.
    Uses external database URLs and optimized settings.
    """
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # Heroku/old url fix
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )
    
    # Use Redis for rate limiting (DigitalOcean App Platform / Heroku)
    # Ensure you have a Redis component attached and the REDIS_URL env var set
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL")


class DevConfig(BaseConfig):
    """
    Development configuration class.
    Enables debug mode and uses a local SQLite database.
    """
    DEBUG = True
    CREATE_DB = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///dev.db"
    
    # Use Redis if configured in .env, otherwise fallback to in-memory storage to suppress warnings
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL") or "memory://"



class TestConfig(BaseConfig):
    """
    Testing configuration class.
    Uses an in-memory database for isolated and fast tests.
    """
    TESTING = True
    DEBUG = True  # Disable force_https in Talisman
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CREATE_DB = True
    WTF_CSRF_ENABLED = False
