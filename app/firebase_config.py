import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os

db = None
auth_client = None
bucket = None

firebase_key_path = os.getenv('FIREBASE_KEY_PATH', './firebase-key.json')

if os.path.exists(firebase_key_path):
    try:
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'air-reservations.appspot.com')
        })
        db = firestore.client()
        auth_client = auth
        bucket = storage.bucket()
        print('✅ Firebase connected')
    except Exception as e:
        print(f'⚠️  Firebase error: {e}')
else:
    print('⚠️  firebase-key.json not found — running without Firebase')

def get_db():
    return db
