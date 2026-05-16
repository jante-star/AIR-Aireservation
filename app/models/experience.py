from firebase_admin import firestore as fs

class Experience:
    COLLECTION = 'experiences'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db: return None
        ref = db.collection(Experience.COLLECTION).document()
        doc = {
            'id': ref.id,
            'hostId': host_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'category': data.get('category', 'other'),
            'price': float(data.get('price', 0)),
            'duration': {
                'value': int(data.get('duration_value', 2)),
                'unit': data.get('duration_unit', 'hours'),
            },
            'maxGroupSize': int(data.get('max_group_size', 10)),
            'location': {
                'address': data.get('address', ''),
                'city': data.get('city', ''),
                'country': data.get('country', ''),
                'latitude': float(data.get('latitude', 0)),
                'longitude': float(data.get('longitude', 0)),
            },
            'images': data.get('images', []),
            'aiConfig': {'enabled': False, 'agentId': ''},
            'ratings': {'average': 0, 'count': 0},
            'status': 'draft',
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        }
        ref.set(doc)
        from app.services.listing_sync import sync_listing
        sync_listing('experience', ref.id, 'create', doc)
        return ref.id

    @staticmethod
    def get_by_id(exp_id):
        from app.firebase_config import db
        if not db: return None
        doc = db.collection(Experience.COLLECTION).document(exp_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_all_published():
        from app.firebase_config import db
        if not db: return []
        docs = db.collection(Experience.COLLECTION).where('status', '==', 'published').stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def get_by_host(host_id):
        from app.firebase_config import db
        if not db: return []
        docs = db.collection(Experience.COLLECTION).where('hostId', '==', host_id).stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def update(exp_id, data):
        from app.firebase_config import db
        if not db: return
        db.collection(Experience.COLLECTION).document(exp_id).update({
            **data,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
        fresh = Experience.get_by_id(exp_id)
        if fresh:
            from app.services.listing_sync import sync_listing
            sync_listing('experience', exp_id, 'update', fresh)

    @staticmethod
    def delete(exp_id):
        from app.firebase_config import db
        if not db: return
        doc = Experience.get_by_id(exp_id)
        db.collection(Experience.COLLECTION).document(exp_id).delete()
        if doc:
            from app.services.listing_sync import sync_listing
            sync_listing('experience', exp_id, 'delete', doc)
