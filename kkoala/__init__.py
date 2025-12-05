from flask import Flask, render_template, session, send_from_directory, Response, url_for, request
from flask_talisman import Talisman
import os
from datetime import datetime
from kkoala.models import User
from dotenv import load_dotenv
import resend

from .routes import register_blueprints
from .extensions import db, bcrypt, migrate, limiter
from .utils import make_csrf_token

load_dotenv()


def create_app(config_class="config.ProdConfig"):
    """
    Application factory function for creating and configuring the Flask app.
    This pattern allows flexible configuration and easier testing.
    """
    # Create the Flask application instance
    app = Flask(__name__, static_folder="static", template_folder="templates")
    # Load configuration from the given config class
    app.config.from_object(config_class)

    # Initialize Flask extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Configure Flask-Talisman for security headers
    # CSP allows inline styles/scripts (needed for Tailwind and FullCalendar)
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts
            'https://cdn.jsdelivr.net',  # FullCalendar CDN
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Required for Tailwind and inline styles
            'https://cdn.jsdelivr.net',
        ],
        'img-src': ["'self'", 'data:', 'blob:'],  # Allow data URIs for favicon inversion
        'font-src': ["'self'", 'https://cdn.jsdelivr.net'],
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
    }
    
    # Only enforce HTTPS in production (not localhost)
    force_https = not app.debug
    
    Talisman(
        app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        force_https=force_https,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        x_content_type_options=True,
        x_xss_protection=True,
        referrer_policy='strict-origin-when-cross-origin',
    )

    # Configure Resend API key for email sending, if set
    resend_key = app.config.get("RESEND_API_KEY")
    if resend_key:
        resend.api_key = resend_key

    # Register a CSRF token generator to run before each request
    app.before_request(make_csrf_token)

    # Custom error handler for 404 Not Found
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    # Custom error handler for 500 Internal Server Error
    @app.errorhandler(500)
    def internal_error(error):
        # Roll back the database session to avoid invalid states
        db.session.rollback()
        return render_template("500.html"), 500

    # Custom error handler for 403 Forbidden
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/img'),
                                   'KantiKoalaLogoVar2.png', mimetype='image/x-icon')

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'robots.txt', mimetype='text/plain')

    @app.route('/sitemap.xml')
    def sitemap():
        """Generate sitemap.xml for SEO with public pages."""
        pages = []
        # Static public pages
        public_routes = [
            ('main.index', 1.0, 'daily'),
            ('main.about', 0.8, 'monthly'),
            ('main.hilfe', 0.7, 'monthly'),
            ('main.lerntimer', 0.8, 'monthly'),
            ('main.lerntipps', 0.8, 'weekly'),
            ('main.datenschutzerklaerung', 0.3, 'yearly'),
        ]
        
        for route, priority, changefreq in public_routes:
            pages.append({
                'loc': url_for(route, _external=True),
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': changefreq,
                'priority': priority
            })
        
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for page in pages:
            sitemap_xml += '  <url>\n'
            sitemap_xml += f'    <loc>{page["loc"]}</loc>\n'
            sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
            sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
            sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
            sitemap_xml += '  </url>\n'
        sitemap_xml += '</urlset>'
        
        return Response(sitemap_xml, mimetype='application/xml')

    # Register all application blueprints (routes)
    register_blueprints(app)

    @app.context_processor
    def inject_dark_mode_setting():
        """
        Injects the user's dark mode preference into all templates.
        Defaults to 'system' if the user is not logged in or has no setting.
        """
        dark_mode = 'system'  # Default value
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user and user.settings:
                dark_mode = user.settings.dark_mode
        return dict(dark_mode_setting=dark_mode)

    # Optionally create all database tables if CREATE_DB is set in config
    if app.config.get("CREATE_DB"):
        with app.app_context():
            db.create_all()

    # For SQLite: ensure foreign key constraints are enforced
    # This PRAGMA must be set for every new connection
    if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(db.text("PRAGMA foreign_keys=ON"))

    # Return the configured Flask app instance
    return app
