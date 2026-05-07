from firebase_admin import firestore as fs

class User:
    COLLECTION = 'users'

    @staticmethod
    def get_by_id(user_id):
        from app.firebase_config import db
        if not db: return None
        doc = db.collection(User.COLLECTION).document(user_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_by_email(email):
        from app.firebase_config import db
        if not db: return None
        docs = db.collection(User.COLLECTION).where('email', '==', email).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    @staticmethod
    def create(user_id, data):
        from app.firebase_config import db
        if not db: return
        db.collection(User.COLLECTION).document(user_id).set({
            'uid': user_id,
            **data,
            'created_at': fs.SERVER_TIMESTAMP,
            'updated_at': fs.SERVER_TIMESTAMP,
        })

    @staticmethod
    def update(user_id, data):
        from app.firebase_config import db
        if not db: return
        db.collection(User.COLLECTION).document(user_id).update({
            **data,
            'updated_at': fs.SERVER_TIMESTAMP,
        })
