from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.user import User
from app.models.home import Home
from app.models.booking import Booking
from app.services.storage_service import StorageService
from app.utils.decorators import login_required

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def profile():
    user = User.get_by_id(session['user_id'])
    listings = Home.get_by_host(session['user_id']) if session.get('role') == 'host' else []
    bookings = Booking.get_by_guest(session['user_id'])
    return render_template('pages/profile.html', user=user, listings=listings, bookings=bookings)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.get_by_id(session['user_id'])
    if request.method == 'POST':
        image_url = user.get('profile_image', '') if user else ''
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            uploaded = StorageService.upload(
                request.files['profile_image'],
                f"profiles/{session['user_id']}"
            )
            if uploaded:
                image_url = uploaded
        User.update(session['user_id'], {
            'name': request.form.get('name', ''),
            'phone': request.form.get('phone', ''),
            'bio': request.form.get('bio', ''),
            'profile_image': image_url,
        })
        session['name'] = request.form.get('name', '')
        return redirect(url_for('profile.profile'))
    return render_template('pages/edit_profile.html', user=user)

@profile_bp.route('/my-listings')
@login_required
def my_listings():
    listings = Home.get_by_host(session['user_id'])
    return render_template('pages/my_listings.html', listings=listings)
