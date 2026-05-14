from firebase_admin import firestore as fs

class Party:
    COLLECTION = 'parties'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db: return None
        ref = db.collection(Party.COLLECTION).document()
        doc = {
            'id': ref.id,
            'hostId': host_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'eventType': data.get('event_type', 'other'),
            'dateTime': data.get('date_time', ''),
            'ticketPrice': float(data.get('ticket_price', 0)),
            'capacity': int(data.get('capacity', 100)),
            'ticketsSold': 0,
            'location': {
                'address': data.get('address', ''),
                'city': data.get('city', ''),
                'country': data.get('country', ''),
                'latitude': float(data.get('latitude', 0)),
                'longitude': float(data.get('longitude', 0)),
            },
            'images': data.get('images', []),
            'aiConfig': {'enabled': False, 'agentId': ''},
            'status': 'draft',
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        }
        ref.set(doc)
        from app.services.listing_sync import sync_listing
        sync_listing('party', ref.id, 'create', doc)
        return ref.id

    @staticmethod
    def get_by_id(party_id):
        from app.firebase_config import db
        if not db: return None
        doc = db.collection(Party.COLLECTION).document(party_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_all_published():
        from app.firebase_config import db
        if not db: return []
        docs = db.collection(Party.COLLECTION).where('status', '==', 'published').stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def update(party_id, data):
        from app.firebase_config import db
        if not db: return
        db.collection(Party.COLLECTION).document(party_id).update({
            **data,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
        fresh = Party.get_by_id(party_id)
        if fresh:
            from app.services.listing_sync import sync_listing
            sync_listing('party', party_id, 'update', fresh)

    @staticmethod
    def delete(party_id):
        from app.firebase_config import db
        if not db: return
        doc = Party.get_by_id(party_id)
        db.collection(Party.COLLECTION).document(party_id).delete()
        if doc:
            from app.services.listing_sync import sync_listing
            sync_listing('party', party_id, 'delete', doc)
