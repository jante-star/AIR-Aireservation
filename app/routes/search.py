from flask import Blueprint, render_template, request
from app.models.home import Home
from app.models.experience import Experience
from app.models.party import Party

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/')
def search():
    q = request.args.get('q', '').strip().lower()
    listing_type = request.args.get('type', 'all')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'newest')

    def matches(listing):
        if q:
            title = listing.get('title', '').lower()
            desc = listing.get('description', '').lower()
            city = listing.get('location', {}).get('city', '').lower()
            if q not in title and q not in desc and q not in city:
                return False
        price = listing.get('price') or listing.get('ticketPrice', 0)
        if min_price and price < min_price:
            return False
        if max_price and price > max_price:
            return False
        return True

    def sort_listings(items):
        if sort == 'price_asc':
            return sorted(items, key=lambda x: x.get('price') or x.get('ticketPrice', 0))
        elif sort == 'price_desc':
            return sorted(items, key=lambda x: x.get('price') or x.get('ticketPrice', 0), reverse=True)
        elif sort == 'rating':
            return sorted(items, key=lambda x: x.get('ratings', {}).get('average', 0), reverse=True)
        return items

    results = {'homes': [], 'experiences': [], 'parties': []}

    if listing_type in ('all', 'homes'):
        results['homes'] = sort_listings([h for h in Home.search() if matches(h)])
    if listing_type in ('all', 'experiences'):
        results['experiences'] = sort_listings([e for e in Experience.get_all_published() if matches(e)])
    if listing_type in ('all', 'parties'):
        results['parties'] = sort_listings([p for p in Party.get_all_published() if matches(p)])

    total = sum(len(v) for v in results.values())
    return render_template('pages/search.html', q=q, results=results, total=total,
                           listing_type=listing_type, sort=sort)
