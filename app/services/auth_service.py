from firebase_admin import auth as firebase_auth
from firebase_admin import firestore as fs
from flask import session

class AuthService:

    @staticmethod
    def register(email, password, user_data):
        try:
            user = firebase_auth.create_user(email=email, password=password)
            from app.firebase_config import db
            if db:
                db.collection('users').document(user.uid).set({
                    'uid': user.uid,
                    'email': email,
                    'role': user_data.get('role', 'guest'),
                    'name': user_data.get('name', ''),
                    'phone': '',
                    'bio': '',
                    'profile_image': '',
                    'created_at': fs.SERVER_TIMESTAMP,
                    'updated_at': fs.SERVER_TIMESTAMP,
                })
            return user
        except firebase_auth.EmailAlreadyExistsError:
            return {'error': 'An account with this email already exists'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def verify_token(token):
        try:
            return firebase_auth.verify_id_token(token)
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def logout():
        session.clear()
