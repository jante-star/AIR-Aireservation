from firebase_admin import firestore as fs


class Service:
    COLLECTION = 'services'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db:
            return None
        ref = db.collection(Service.COLLECTION).document()
        doc = {
            'id': ref.id,
            'hostId': host_id,
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'category': data.get('category', 'other'),
            'price': float(data.get('price', 0)),
            'priceUnit': data.get('priceUnit', 'session'),
            'location': data.get('location', {}),
            'images': data.get('images', []),
            'ratings': {'average': 0.0, 'count': 0},
            'status': data.get('status', 'published'),
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        }
        ref.set(doc)
        return ref.id

    @staticmethod
    def get_by_id(service_id):
        from app.firebase_config import db
        if not db:
            return None
        doc = db.collection(Service.COLLECTION).document(service_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_all_published():
        from app.firebase_config import db
        if not db:
            return []
        docs = (db.collection(Service.COLLECTION)
                .where('status', '==', 'published')
                .stream())
        return [d.to_dict() for d in docs]

    @staticmethod
    def search(city=None, category=None):
        from app.firebase_config import db
        if not db:
            return []
        query = db.collection(Service.COLLECTION).where('status', '==', 'published')
        docs = [d.to_dict() for d in query.stream()]
        if city:
            docs = [d for d in docs if city.lower() in d.get('location', {}).get('city', '').lower()]
        if category:
            docs = [d for d in docs if d.get('category') == category]
        return docs
