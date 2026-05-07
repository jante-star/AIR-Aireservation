from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.experience import Experience
from app.services.storage_service import StorageService
from app.utils.decorators import login_required, host_required

experiences_bp = Blueprint('experiences', __name__, url_prefix='/experiences')

@experiences_bp.route('/')
def list_experiences():
    experiences = Experience.get_all_published()
    return render_template('pages/experiences_list.html', experiences=experiences)

@experiences_bp.route('/<exp_id>')
def view_experience(exp_id):
    experience = Experience.get_by_id(exp_id)
    if not experience:
        return render_template('errors/404.html'), 404
    return render_template('pages/listing_detail.html', listing=experience, listing_type='experience')

@experiences_bp.route('/create', methods=['GET', 'POST'])
@login_required
@host_required
def create_experience():
    if request.method == 'POST':
        images = []
        if 'images' in request.files:
            images = StorageService.upload_multiple(
                request.files.getlist('images'),
                f"experiences/{session['user_id']}"
            )
        exp_id = Experience.create(session['user_id'], {
            **request.form.to_dict(),
            'images': images,
            'ai_enabled': request.form.get('ai_enabled') == 'on',
        })
        return redirect(url_for('experiences.view_experience', exp_id=exp_id))
    return render_template('pages/create_listing.html', listing_type='experience')
