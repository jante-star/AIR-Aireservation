from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.party import Party
from app.services.storage_service import StorageService
from app.utils.decorators import login_required, host_required

parties_bp = Blueprint('parties', __name__, url_prefix='/parties')

@parties_bp.route('/')
def list_parties():
    parties = Party.get_all_published()
    return render_template('pages/parties_list.html', parties=parties)

@parties_bp.route('/<party_id>')
def view_party(party_id):
    party = Party.get_by_id(party_id)
    if not party:
        return render_template('errors/404.html'), 404
    return render_template('pages/listing_detail.html', listing=party, listing_type='party')

@parties_bp.route('/create', methods=['GET', 'POST'])
@login_required
@host_required
def create_party():
    if request.method == 'POST':
        images = []
        if 'images' in request.files:
            images = StorageService.upload_multiple(
                request.files.getlist('images'),
                f"parties/{session['user_id']}"
            )
        party_id = Party.create(session['user_id'], {
            **request.form.to_dict(),
            'images': images,
            'ai_enabled': request.form.get('ai_enabled') == 'on',
        })
        return redirect(url_for('parties.view_party', party_id=party_id))
    return render_template('pages/create_listing.html', listing_type='party')
