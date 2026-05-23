from flask import Blueprint, render_template, request
from app.models.car import Car

cars_bp = Blueprint('cars', __name__, url_prefix='/cars')

PLACEHOLDER_CARS = [
    {'id': 'c1', 'make': 'Toyota', 'model': 'Corolla', 'year': 2022, 'category': 'economy',
     'price': 45, 'location': {'city': 'Kingston', 'country': 'Jamaica', 'lat': 17.9972, 'lng': -76.7936},
     'seats': 5, 'features': ['AC', 'Bluetooth', 'Automatic'], 'images': [],
     'ratings': {'average': 4.8, 'count': 22}, 'status': 'available'},
    {'id': 'c2', 'make': 'Nissan', 'model': 'X-Trail', 'year': 2023, 'category': 'suv',
     'price': 75, 'location': {'city': 'Montego Bay', 'country': 'Jamaica', 'lat': 18.4762, 'lng': -77.8939},
     'seats': 7, 'features': ['AC', '4WD', 'Sunroof'], 'images': [],
     'ratings': {'average': 4.7, 'count': 15}, 'status': 'available'},
    {'id': 'c3', 'make': 'Toyota', 'model': 'Hiace', 'year': 2021, 'category': 'van',
     'price': 90, 'location': {'city': 'Kingston', 'country': 'Jamaica', 'lat': 17.9972, 'lng': -76.7936},
     'seats': 12, 'features': ['AC', 'Large luggage space'], 'images': [],
     'ratings': {'average': 4.6, 'count': 11}, 'status': 'available'},
    {'id': 'c4', 'make': 'Honda', 'model': 'Vezel', 'year': 2023, 'category': 'suv',
     'price': 60, 'location': {'city': 'Ocho Rios', 'country': 'Jamaica', 'lat': 18.4046, 'lng': -77.1036},
     'seats': 5, 'features': ['AC', 'Backup cam', 'Bluetooth'], 'images': [],
     'ratings': {'average': 4.9, 'count': 8}, 'status': 'available'},
    {'id': 'c5', 'make': 'Kia', 'model': 'Seltos', 'year': 2022, 'category': 'suv',
     'price': 65, 'location': {'city': 'Mandeville', 'country': 'Jamaica', 'lat': 18.0422, 'lng': -77.5043},
     'seats': 5, 'features': ['AC', 'Keyless entry', 'Bluetooth'], 'images': [],
     'ratings': {'average': 4.8, 'count': 19}, 'status': 'available'},
]


@cars_bp.route('/')
def list_cars():
    city = request.args.get('city', '').strip()
    category = request.args.get('category', '').strip()
    cars = Car.search(city=city or None, category=category or None)
    if not cars:
        cars = PLACEHOLDER_CARS
        if city:
            cars = [c for c in cars if city.lower() in c['location']['city'].lower()]
        if category:
            cars = [c for c in cars if c['category'] == category]
    return render_template('pages/cars_list.html', cars=cars, city=city, category=category)


@cars_bp.route('/<car_id>')
def view_car(car_id):
    car = Car.get_by_id(car_id)
    if not car:
        car = next((c for c in PLACEHOLDER_CARS if c['id'] == car_id), None)
    if not car:
        from flask import abort
        abort(404)
    return render_template('pages/cars_list.html', cars=PLACEHOLDER_CARS, selected=car)
