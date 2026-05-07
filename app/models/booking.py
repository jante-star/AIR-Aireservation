from firebase_admin import firestore as fs

class Booking:
    COLLECTION = 'bookings'

    @staticmethod
    def create(guest_id, listing_id, listing_type, data):
        from app.firebase_config import db
        if not db: return None
        ref = db.collection(Booking.COLLECTION).document()
        ref.set({
            'id': ref.id,
            'guestId': guest_id,
            'listingId': listing_id,
            'listingType': listing_type,
            'checkIn': data.get('check_in', ''),
            'checkOut': data.get('check_out', ''),
            'guests': int(data.get('guests', 1)),
            'totalPrice': float(data.get('total_price', 0)),
            'status': 'pending',
            'paymentStatus': 'pending',
            'paymentId': data.get('payment_id', ''),
            'notes': data.get('notes', ''),
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
        return ref.id

    @staticmethod
    def get_by_id(booking_id):
        from app.firebase_config import db
        if not db: return None
        doc = db.collection(Booking.COLLECTION).document(booking_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_by_guest(guest_id):
        from app.firebase_config import db
        if not db: return []
        docs = db.collection(Booking.COLLECTION).where('guestId', '==', guest_id).stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def update_status(booking_id, status):
        from app.firebase_config import db
        if not db: return
        db.collection(Booking.COLLECTION).document(booking_id).update({
            'status': status,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
