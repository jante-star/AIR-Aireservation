from flask import Flask, render_template, session
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    from app.routes.auth import auth_bp
    from app.routes.homes import homes_bp
    from app.routes.experiences import experiences_bp
    from app.routes.parties import parties_bp
    from app.routes.bookings import bookings_bp
    from app.routes.profile import profile_bp
    from app.routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(homes_bp)
    app.register_blueprint(experiences_bp)
    app.register_blueprint(parties_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)

    @app.route('/')
    def index():
        from app.models.home import Home
        featured = Home.get_featured() if Home else []
        return render_template('pages/home.html', featured_listings=featured)

    @app.route('/health')
    def health():
        return {'status': 'healthy', 'app': 'Air — AI Reservations'}, 200

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
