from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.booking import Booking
from app.models.home import Home
from app.utils.decorators import login_required

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bookings_bp.route('/create', methods=['POST'])
@login_required
def create_booking():
    listing_id = request.form.get('listing_id')
    listing_type = request.form.get('listing_type', 'home')
    guests = int(request.form.get('guests', 1))
    check_in = request.form.get('check_in', '')
    check_out = request.form.get('check_out', '')
    listing = Home.get_by_id(listing_id)
    total_price = listing.get('price', 0) * guests if listing else 0
    booking_id = Booking.create(session['user_id'], listing_id, listing_type, {
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'total_price': total_price,
    })
    return redirect(url_for('bookings.confirmation', booking_id=booking_id))

@bookings_bp.route('/<booking_id>/confirmation')
@login_required
def confirmation(booking_id):
    booking = Booking.get_by_id(booking_id)
    if not booking or booking.get('guestId') != session['user_id']:
        return redirect(url_for('index'))
    Booking.update_status(booking_id, 'confirmed')
    listing = Home.get_by_id(booking.get('listingId', ''))
    return render_template('pages/booking_confirmation.html', booking=booking, listing=listing)

@bookings_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.get_by_guest(session['user_id'])
    return render_template('pages/my_bookings.html', bookings=bookings)

@bookings_bp.route('/api/ai/start-call', methods=['POST'])
@login_required
def start_ai_call():
    from app.services.ai_service import RetellAIService
    data = request.get_json()
    agent_id = data.get('agent_id')
    listing_id = data.get('listing_id')
    token = RetellAIService.create_call_token(agent_id, session['user_id'], listing_id)
    if token:
        return jsonify({'access_token': token})
    return jsonify({'error': 'Could not start call'}), 500
