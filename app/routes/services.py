from flask import Blueprint, render_template, request
from app.models.service import Service

services_bp = Blueprint('services', __name__, url_prefix='/services')

PLACEHOLDER_SERVICES = [
    {'id': 's1', 'title': 'Jamaica Property Photography', 'category': 'photography', 'price': 150, 'priceUnit': 'session',
     'description': 'Professional real estate and vacation rental photography. Drone shots included. Edited gallery within 24 hours.',
     'location': {'city': 'Kingston', 'country': 'Jamaica'}, 'ratings': {'average': 4.9, 'count': 16}, 'images': [], 'status': 'published'},
    {'id': 's2', 'title': 'Event & Wedding Photography', 'category': 'photography', 'price': 200, 'priceUnit': 'event',
     'description': 'Full-day event coverage with 200+ edited photos delivered within 48 hours.',
     'location': {'city': 'Montego Bay', 'country': 'Jamaica'}, 'ratings': {'average': 5.0, 'count': 9}, 'images': [], 'status': 'published'},
    {'id': 's3', 'title': 'Private Jerk Chef Experience', 'category': 'catering', 'price': 80, 'priceUnit': 'person',
     'description': 'Authentic Jamaican jerk BBQ cooked right at your villa by a local chef. Includes rice & peas, festival, and rum punch.',
     'location': {'city': 'Ocho Rios', 'country': 'Jamaica'}, 'ratings': {'average': 4.8, 'count': 27}, 'images': [], 'status': 'published'},
    {'id': 's4', 'title': 'Caribbean Fusion Catering', 'category': 'catering', 'price': 65, 'priceUnit': 'person',
     'description': 'Full-service catering for groups of 10–100. Custom menus blending Jamaican, Caribbean, and international cuisines.',
     'location': {'city': 'Kingston', 'country': 'Jamaica'}, 'ratings': {'average': 4.7, 'count': 21}, 'images': [], 'status': 'published'},
    {'id': 's5', 'title': 'Breakfast in Paradise', 'category': 'catering', 'price': 45, 'priceUnit': 'person',
     'description': 'Fresh Jamaican breakfast served poolside or on the beach. Ackee & saltfish, bammy, fresh fruit, and Blue Mountain coffee.',
     'location': {'city': 'Negril', 'country': 'Jamaica'}, 'ratings': {'average': 4.9, 'count': 38}, 'images': [], 'status': 'published'},
]


@services_bp.route('/')
def list_services():
    city = request.args.get('city', '').strip()
    category = request.args.get('category', '').strip()
    services = Service.search(city=city or None, category=category or None)
    if not services:
        services = PLACEHOLDER_SERVICES
    return render_template('pages/services_list.html', services=services, city=city, category=category)


@services_bp.route('/<service_id>')
def view_service(service_id):
    service = Service.get_by_id(service_id)
    if not service:
        service = next((s for s in PLACEHOLDER_SERVICES if s['id'] == service_id), None)
    if not service:
        from flask import abort
        abort(404)
    return render_template('pages/listing_detail.html', listing=service, listing_type='service')
