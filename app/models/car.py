from firebase_admin import firestore as fs


class Car:
    COLLECTION = 'cars'

    @staticmethod
    def create(host_id, data):
        from app.firebase_config import db
        if not db:
            return None
        ref = db.collection(Car.COLLECTION).document()
        doc = {
            'id': ref.id,
            'hostId': host_id,
            'make': data.get('make', ''),
            'model': data.get('model', ''),
            'year': int(data.get('year', 2023)),
            'category': data.get('category', 'economy'),
            'price': float(data.get('price', 0)),
            'location': data.get('location', {}),
            'images': data.get('images', []),
            'seats': int(data.get('seats', 5)),
            'features': data.get('features', []),
            'ratings': {'average': 0.0, 'count': 0},
            'status': data.get('status', 'available'),
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        }
        ref.set(doc)
        return ref.id

    @staticmethod
    def get_by_id(car_id):
        from app.firebase_config import db
        if not db:
            return None
        doc = db.collection(Car.COLLECTION).document(car_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_all_available():
        from app.firebase_config import db
        if not db:
            return []
        docs = (db.collection(Car.COLLECTION)
                .where('status', '==', 'available')
                .stream())
        return [d.to_dict() for d in docs]

    @staticmethod
    def search(city=None, category=None):
        from app.firebase_config import db
        if not db:
            return []
        docs = [d.to_dict() for d in db.collection(Car.COLLECTION).stream()]
        if city:
            docs = [d for d in docs if city.lower() in d.get('location', {}).get('city', '').lower()]
        if category:
            docs = [d for d in docs if d.get('category') == category]
        return docs
