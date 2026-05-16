import requests
import os

BASE_URL = os.getenv('RETELL_API_BASE_URL', 'https://api.retellai.com')

KB_IDS = {
    'home':       os.getenv('RETELL_KB_HOMES_ID', ''),
    'experience': os.getenv('RETELL_KB_EXPERIENCES_ID', ''),
    'party':      os.getenv('RETELL_KB_PARTIES_ID', ''),
}

COLLECTION_MAP = {
    'home':       'homes',
    'experience': 'experiences',
    'party':      'parties',
}


class RetellKBService:

    @staticmethod
    def _headers():
        return {
            'Authorization': f"Bearer {os.getenv('RETELL_API_KEY', '')}",
            'Content-Type': 'application/json',
        }

    # ── Document renderer ────────────────────────────────────────────────────

    @staticmethod
    def _render_doc(listing_type, data):
        """Return {title, text} for a Retell KB text source."""
        loc = data.get('location') or {}
        city = loc.get('city', '')
        country = loc.get('country', '')
        address = loc.get('address', '')
        lid = data.get('id', '')

        if listing_type == 'home':
            amenities = ', '.join(data.get('amenities') or []) or 'None listed'
            ratings = data.get('ratings') or {}
            source_note = 'google_places' if data.get('source') == 'google_places' else 'air'
            text = (
                f"LISTING_ID: {lid}\n"
                f"TYPE: home\n"
                f"CATEGORY: {data.get('category', 'villa')}    SOURCE: {source_note}\n"
                f"PRICE: ${data.get('price', 0):.0f}/night\n"
                f"CAPACITY: {data.get('bedrooms', 1)} bedrooms, {data.get('bathrooms', 1)} bathrooms\n"
                f"LOCATION: {address}, {city}, {country}\n"
                f"AMENITIES: {amenities}\n"
                f"RATING: {ratings.get('average', 0)} ({ratings.get('count', 0)} reviews)\n"
                f"DESCRIPTION:\n{data.get('description', '')}"
            )
            title = f"{data.get('title', 'Unnamed')} — {city}"

        elif listing_type == 'experience':
            dur = data.get('duration') or {}
            text = (
                f"LISTING_ID: {lid}\n"
                f"TYPE: experience\n"
                f"CATEGORY: {data.get('category', 'other')}\n"
                f"PRICE: ${data.get('price', 0):.0f}/person\n"
                f"DURATION: {dur.get('value', '')} {dur.get('unit', '')}\n"
                f"GROUP SIZE: up to {data.get('maxGroupSize', '')}\n"
                f"LOCATION: {address}, {city}, {country}\n"
                f"DESCRIPTION:\n{data.get('description', '')}"
            )
            title = f"{data.get('title', 'Unnamed')} — {city} (experience)"

        else:  # party / event
            capacity = int(data.get('capacity', 0))
            tickets_sold = int(data.get('ticketsSold', 0))
            left = max(capacity - tickets_sold, 0)
            text = (
                f"LISTING_ID: {lid}\n"
                f"TYPE: event\n"
                f"EVENT_TYPE: {data.get('eventType', 'other')}\n"
                f"DATE: {data.get('dateTime', 'TBD')}\n"
                f"TICKET PRICE: ${data.get('ticketPrice', 0):.0f}\n"
                f"CAPACITY: {capacity} ({left} tickets left)\n"
                f"LOCATION: {address}, {city}, {country}\n"
                f"DESCRIPTION:\n{data.get('description', '')}"
            )
            title = f"{data.get('title', 'Unnamed')} — {city} (event)"

        return {'title': title, 'text': text}

    # ── CRUD on Retell knowledge-base sources ────────────────────────────────

    @staticmethod
    def add_listing(listing_type, listing_id, listing_data):
        """Add a listing as a text source in the right category KB.
        Persists the returned source_id back to Firestore so future updates
        know which source to replace.  Returns the source_id or None."""
        kb_id = KB_IDS.get(listing_type)
        if not kb_id:
            print(f'[RetellKB] No KB ID configured for {listing_type!r}')
            return None

        doc = RetellKBService._render_doc(listing_type, listing_data)
        payload = {'knowledge_base_texts': [doc]}
        try:
            r = requests.post(
                f'{BASE_URL}/add-knowledge-base-sources/{kb_id}',
                json=payload,
                headers=RetellKBService._headers(),
                timeout=15,
            )
            if r.status_code not in (200, 201):
                print(f'[RetellKB] add_listing failed {r.status_code}: {r.text[:200]}')
                return None
            sources = r.json().get('knowledge_base_sources', [])
            source_id = sources[-1].get('source_id') if sources else None
            if source_id:
                RetellKBService._persist_source_id(listing_type, listing_id, source_id)
            return source_id
        except Exception as e:
            print(f'[RetellKB] add_listing error: {e}')
            return None

    @staticmethod
    def remove_listing(listing_type, listing_id, source_id):
        """Delete a source from the Retell KB by its source_id."""
        kb_id = KB_IDS.get(listing_type)
        if not kb_id or not source_id:
            return
        try:
            r = requests.delete(
                f'{BASE_URL}/delete-knowledge-base-source/{kb_id}/{source_id}',
                headers=RetellKBService._headers(),
                timeout=15,
            )
            if r.status_code not in (200, 204):
                print(f'[RetellKB] remove_listing failed {r.status_code}: {r.text[:200]}')
        except Exception as e:
            print(f'[RetellKB] remove_listing error: {e}')

    @staticmethod
    def update_listing(listing_type, listing_id, listing_data):
        """Replace an existing KB source: delete old, add fresh."""
        old_source_id = listing_data.get('retellSourceId', '')
        if old_source_id:
            RetellKBService.remove_listing(listing_type, listing_id, old_source_id)
        return RetellKBService.add_listing(listing_type, listing_id, listing_data)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _persist_source_id(listing_type, listing_id, source_id):
        try:
            from app.firebase_config import db
            collection = COLLECTION_MAP.get(listing_type, 'homes')
            if db:
                db.collection(collection).document(listing_id).update(
                    {'retellSourceId': source_id}
                )
        except Exception as e:
            print(f'[RetellKB] persist source_id error: {e}')
