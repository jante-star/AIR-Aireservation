from firebase_admin import firestore as fs

class Home:
    COLLECTION = 'homes'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db: return None
        ref = db.collection(Home.COLLECTION).document()
        ref.set({
            'id': ref.id,
            'hostId': host_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category', 'villa'),
            'price': float(data.get('price', 0)),
            'bedrooms': int(data.get('bedrooms', 1)),
            'bathrooms': int(data.get('bathrooms', 1)),
            'location': {
                'address': data.get('address', ''),
                'city': data.get('city', ''),
                'country': data.get('country', ''),
                'latitude': float(data.get('latitude', 0)),
                'longitude': float(data.get('longitude', 0)),
            },
            'amenities': data.get('amenities', []),
            'images': data.get('images', []),
            'aiConfig': {
                'enabled': data.get('ai_enabled', False),
                'agentId': data.get('ai_agent_id', ''),
            },
            'ratings': {'average': 0, 'count': 0},
            'status': 'draft',
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
        return ref.id

    @staticmethod
    def get_by_id(home_id):
        from app.firebase_config import db
        if not db: return None
        doc = db.collection(Home.COLLECTION).document(home_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_by_host(host_id):
        from app.firebase_config import db
        if not db: return []
        docs = db.collection(Home.COLLECTION).where('hostId', '==', host_id).stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def get_featured(limit=8):
        from app.firebase_config import db
        if not db: return []
        docs = (db.collection(Home.COLLECTION)
                  .where('status', '==', 'published')
                  .limit(limit).stream())
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def search(filters=None):
        from app.firebase_config import db
        if not db: return []
        if filters is None: filters = {}
        query = db.collection(Home.COLLECTION).where('status', '==', 'published')
        results = [doc.to_dict() for doc in query.stream()]
        if filters.get('city'):
            results = [r for r in results if filters['city'].lower() in r.get('location', {}).get('city', '').lower()]
        if filters.get('min_price'):
            results = [r for r in results if r.get('price', 0) >= float(filters['min_price'])]
        if filters.get('max_price'):
            results = [r for r in results if r.get('price', 0) <= float(filters['max_price'])]
        return results

    @staticmethod
    def update(home_id, data):
        from app.firebase_config import db
        if not db: return
        db.collection(Home.COLLECTION).document(home_id).update({
            **data,
            'updated_at': fs.SERVER_TIMESTAMP,
        })

    @staticmethod
    def delete(home_id):
        from app.firebase_config import db
        if not db: return
        db.collection(Home.COLLECTION).document(home_id).delete()
