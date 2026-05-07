from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.home import Home
from app.services.storage_service import StorageService
from app.utils.decorators import login_required, host_required

homes_bp = Blueprint('homes', __name__, url_prefix='/homes')

@homes_bp.route('/')
def list_homes():
    filters = {
        'city': request.args.get('city', ''),
        'min_price': request.args.get('min_price'),
        'max_price': request.args.get('max_price'),
    }
    homes = Home.search(filters)
    return render_template('pages/homes_list.html', homes=homes)

@homes_bp.route('/<home_id>')
def view_home(home_id):
    home = Home.get_by_id(home_id)
    if not home:
        return render_template('errors/404.html'), 404
    return render_template('pages/listing_detail.html', listing=home, listing_type='home')

@homes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@host_required
def create_home():
    if request.method == 'POST':
        images = []
        if 'images' in request.files:
            images = StorageService.upload_multiple(
                request.files.getlist('images'),
                f"homes/{session['user_id']}"
            )
        home_id = Home.create(session['user_id'], {
            **request.form.to_dict(),
            'images': images,
            'ai_enabled': request.form.get('ai_enabled') == 'on',
            'amenities': request.form.getlist('amenities'),
        })
        return redirect(url_for('homes.view_home', home_id=home_id))
    return render_template('pages/create_listing.html', listing_type='home')

@homes_bp.route('/<home_id>/edit', methods=['GET', 'POST'])
@login_required
@host_required
def edit_home(home_id):
    home = Home.get_by_id(home_id)
    if not home or home.get('hostId') != session['user_id']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        Home.update(home_id, {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price', 0)),
        })
        return redirect(url_for('homes.view_home', home_id=home_id))
    return render_template('pages/create_listing.html', listing=home, listing_type='home')

@homes_bp.route('/<home_id>/publish', methods=['POST'])
@login_required
@host_required
def publish_home(home_id):
    home = Home.get_by_id(home_id)
    if home and home.get('hostId') == session['user_id']:
        Home.update(home_id, {'status': 'published'})
    return redirect(url_for('homes.view_home', home_id=home_id))
