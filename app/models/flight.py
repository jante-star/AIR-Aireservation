from firebase_admin import firestore as fs


class Flight:
    COLLECTION = 'flights'

    @staticmethod
    def create(data):
        from app.firebase_config import db
        if not db:
            return None
        ref = db.collection(Flight.COLLECTION).document()
        doc = {
            'id': ref.id,
            'airline': data.get('airline', ''),
            'flightNumber': data.get('flightNumber', ''),
            'origin': data.get('origin', {}),
            'destination': data.get('destination', {}),
            'departure': data.get('departure', ''),
            'arrival': data.get('arrival', ''),
            'price': float(data.get('price', 0)),
            'seats': int(data.get('seats', 0)),
            'status': data.get('status', 'available'),
            'created_at': fs.SERVER_TIMESTAMP,
        }
        ref.set(doc)
        return ref.id

    @staticmethod
    def get_by_id(flight_id):
        from app.firebase_config import db
        if not db:
            return None
        doc = db.collection(Flight.COLLECTION).document(flight_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def search(origin_city=None, dest_city=None):
        from app.firebase_config import db
        if not db:
            return []
        docs = [d.to_dict() for d in db.collection(Flight.COLLECTION).stream()]
        if origin_city:
            docs = [d for d in docs if origin_city.lower() in d.get('origin', {}).get('city', '').lower()]
        if dest_city:
            docs = [d for d in docs if dest_city.lower() in d.get('destination', {}).get('city', '').lower()]
        return docs

    @staticmethod
    def get_all():
        from app.firebase_config import db
        if not db:
            return []
        return [d.to_dict() for d in db.collection(Flight.COLLECTION).stream()]
