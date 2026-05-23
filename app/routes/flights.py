from flask import Blueprint, render_template, request
from app.models.flight import Flight

flights_bp = Blueprint('flights', __name__, url_prefix='/flights')

PLACEHOLDER_FLIGHTS = [
    {'id': 'f1', 'airline': 'Caribbean Airlines', 'flightNumber': 'BW401',
     'origin': {'city': 'Kingston', 'iata': 'KIN', 'lat': 17.9357, 'lng': -76.7925},
     'destination': {'city': 'Miami', 'iata': 'MIA', 'lat': 25.7959, 'lng': -80.2870},
     'departure': '2026-07-01T08:00', 'arrival': '2026-07-01T09:50',
     'price': 185, 'seats': 42, 'duration': '1h 50m', 'status': 'available'},
    {'id': 'f2', 'airline': 'Caribbean Airlines', 'flightNumber': 'BW501',
     'origin': {'city': 'Montego Bay', 'iata': 'MBJ', 'lat': 18.5036, 'lng': -77.9136},
     'destination': {'city': 'New York', 'iata': 'JFK', 'lat': 40.6413, 'lng': -73.7781},
     'departure': '2026-07-02T10:00', 'arrival': '2026-07-02T13:45',
     'price': 280, 'seats': 28, 'duration': '3h 45m', 'status': 'available'},
    {'id': 'f3', 'airline': 'Air Canada', 'flightNumber': 'AC984',
     'origin': {'city': 'Kingston', 'iata': 'KIN', 'lat': 17.9357, 'lng': -76.7925},
     'destination': {'city': 'Toronto', 'iata': 'YYZ', 'lat': 43.6777, 'lng': -79.6248},
     'departure': '2026-07-03T14:00', 'arrival': '2026-07-03T18:10',
     'price': 320, 'seats': 15, 'duration': '4h 10m', 'status': 'available'},
    {'id': 'f4', 'airline': 'British Airways', 'flightNumber': 'BA2157',
     'origin': {'city': 'Montego Bay', 'iata': 'MBJ', 'lat': 18.5036, 'lng': -77.9136},
     'destination': {'city': 'London', 'iata': 'LHR', 'lat': 51.4700, 'lng': -0.4543},
     'departure': '2026-07-04T22:00', 'arrival': '2026-07-05T07:30',
     'price': 650, 'seats': 8, 'duration': '9h 30m', 'status': 'available'},
    {'id': 'f5', 'airline': 'Copa Airlines', 'flightNumber': 'CM329',
     'origin': {'city': 'Kingston', 'iata': 'KIN', 'lat': 17.9357, 'lng': -76.7925},
     'destination': {'city': 'Panama City', 'iata': 'PTY', 'lat': 9.0714, 'lng': -79.3835},
     'departure': '2026-07-05T07:30', 'arrival': '2026-07-05T10:15',
     'price': 290, 'seats': 22, 'duration': '2h 45m', 'status': 'available'},
]


@flights_bp.route('/')
def list_flights():
    origin = request.args.get('from', '').strip()
    destination = request.args.get('to', '').strip()
    flights = Flight.search(origin_city=origin or None, dest_city=destination or None)
    if not flights:
        flights = PLACEHOLDER_FLIGHTS
        if origin:
            flights = [f for f in flights if origin.lower() in f['origin']['city'].lower()]
        if destination:
            flights = [f for f in flights if destination.lower() in f['destination']['city'].lower()]
    return render_template('pages/flights_list.html', flights=flights, origin=origin, destination=destination)


@flights_bp.route('/<flight_id>')
def view_flight(flight_id):
    flight = Flight.get_by_id(flight_id)
    if not flight:
        flight = next((f for f in PLACEHOLDER_FLIGHTS if f['id'] == flight_id), None)
    if not flight:
        from flask import abort
        abort(404)
    return render_template('pages/flights_list.html', flights=[flight], selected=flight)
