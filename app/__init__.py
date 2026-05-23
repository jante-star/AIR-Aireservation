from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(config_class)
    CORS(app)

    from app.routes.auth import auth_bp
    from app.routes.homes import homes_bp
    from app.routes.experiences import experiences_bp
    from app.routes.parties import parties_bp
    from app.routes.bookings import bookings_bp
    from app.routes.profile import profile_bp
    from app.routes.search import search_bp
    from app.routes.retell_webhook import retell_bp
    from app.routes.services import services_bp
    from app.routes.flights import flights_bp
    from app.routes.cars import cars_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(homes_bp)
    app.register_blueprint(experiences_bp)
    app.register_blueprint(parties_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(retell_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(cars_bp)

    @app.route('/')
    def index():
        from app.models.home import Home
        from app.models.experience import Experience
        homes, experiences = [], []
        try:
            homes = Home.get_featured() or []
        except Exception:
            pass
        try:
            experiences = Experience.get_all_published()[:6] or []
        except Exception:
            pass
        return render_template('pages/home.html', homes=homes, experiences=experiences)

    @app.route('/api/search')
    def api_search():
        category = request.args.get('category', 'homes')
        city = request.args.get('city', '').strip()
        fmt = request.args.get('fmt', '')

        pins = []
        results = []

        try:
            if category == 'homes':
                from app.models.home import Home
                items = Home.search(city=city) if city else (Home.get_featured() or [])
                for h in items:
                    loc = h.get('location', {})
                    if loc.get('latitude') and loc.get('longitude'):
                        pins.append({'lat': loc['latitude'], 'lng': loc['longitude'],
                                     'price': h.get('price', 0), 'title': h.get('title', ''),
                                     'url': '/homes/' + h.get('id', '')})
                results = items
            elif category == 'experiences':
                from app.models.experience import Experience
                items = Experience.get_all_published()
                for e in items:
                    loc = e.get('location', {})
                    if loc.get('latitude') and loc.get('longitude'):
                        pins.append({'lat': loc['latitude'], 'lng': loc['longitude'],
                                     'price': e.get('price', 0), 'title': e.get('title', ''),
                                     'url': '/experiences/' + e.get('id', '')})
                results = items
            elif category == 'services':
                from app.models.service import Service
                items = Service.search(city=city or None)
                for s in items:
                    loc = s.get('location', {})
                    if loc.get('lat') and loc.get('lng'):
                        pins.append({'lat': loc['lat'], 'lng': loc['lng'],
                                     'price': s.get('price', 0), 'title': s.get('title', ''),
                                     'url': '/services/' + s.get('id', '')})
                results = items
            elif category == 'cars':
                from app.models.car import Car
                items = Car.search(city=city or None)
                for c in items:
                    loc = c.get('location', {})
                    if loc.get('lat') and loc.get('lng'):
                        pins.append({'lat': loc['lat'], 'lng': loc['lng'],
                                     'price': c.get('price', 0),
                                     'title': str(c.get('year', '')) + ' ' + c.get('make', '') + ' ' + c.get('model', ''),
                                     'url': '/cars/' + c.get('id', '')})
                results = items
        except Exception:
            pass

        return jsonify({'pins': pins, 'count': len(results)})

    @app.route('/health')
    def health():
        return {'status': 'healthy', 'app': 'Spot — AI Reservations'}, 200

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
