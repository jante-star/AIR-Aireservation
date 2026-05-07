from firebase_admin import firestore as fs

class Party:
    COLLECTION = 'parties'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db: return None
        ref = db.collection(Party.COLLECTION).document()
        ref.set({
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
            'aiConfig': {
                'enabled': data.get('ai_enabled', False),
                'agentId': data.get('ai_agent_id', ''),
            },
            'status': 'draft',
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
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
