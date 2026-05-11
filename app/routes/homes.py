from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.home import Home
from app.services.storage_service import StorageService
from app.services.ai_service import RetellAIService
from app.services.places_service import PlacesService
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
    # Auto-provision a Retell AI agent for this listing if one doesn't exist yet
    agent_id = RetellAIService.get_or_create_agent(home_id, 'home', home)
    if agent_id:
        if not home.get('aiConfig'):
            home['aiConfig'] = {}
        home['aiConfig']['enabled'] = True
        home['aiConfig']['agentId'] = agent_id
    return render_template('pages/listing_detail.html', listing=home, listing_type='home')

@homes_bp.route('/import-from-places', methods=['GET'])
@login_required
@host_required
def import_from_places():
    """Search Google Places for hotels/accommodations and display results."""
    query = request.args.get('q', 'hotels')
    location = request.args.get('location', '')
    results = PlacesService.search_accommodations(query, location)
    return render_template('pages/places_import.html', results=results, query=query, location=location)

@homes_bp.route('/import-from-places/<place_id>', methods=['POST'])
@login_required
@host_required
def save_place_as_home(place_id):
    """Fetch full Place details and save as a published home listing."""
    place_data = PlacesService.get_place_details(place_id)
    if not place_data:
        return redirect(url_for('homes.import_from_places'))
    home_id = Home.create_from_place(session['user_id'], place_data)
    return redirect(url_for('homes.view_home', home_id=home_id))

@homes_bp.route('/places-photo/<photo_ref>')
def places_photo(photo_ref):
    """Proxy Google Places photos so the API key stays server-side."""
    from flask import Response
    import requests as req
    url = PlacesService.get_photo_url(photo_ref, max_width=800)
    try:
        r = req.get(url, timeout=10, stream=True)
        return Response(r.content, content_type=r.headers.get('Content-Type', 'image/jpeg'))
    except Exception:
        return '', 404

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
