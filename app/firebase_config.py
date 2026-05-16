import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os

db = None
auth_client = None
bucket = None

firebase_key_path = os.getenv('FIREBASE_KEY_PATH', './firebase-key.json')
firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET', '')

if os.path.exists(firebase_key_path):
    try:
        cred = credentials.Certificate(firebase_key_path)
        init_options = {}
        if firebase_storage_bucket:
            init_options['storageBucket'] = firebase_storage_bucket
        firebase_admin.initialize_app(cred, init_options)
        db = firestore.client()
        auth_client = auth
        if firebase_storage_bucket:
            bucket = storage.bucket()
        print('✅ Firebase connected')
        if not firebase_storage_bucket:
            print('⚠️  FIREBASE_STORAGE_BUCKET not set — image uploads disabled')
    except Exception as e:
        print(f'⚠️  Firebase error: {e}')
else:
    print('⚠️  firebase-key.json not found — running without Firebase')
    print('   Set FIREBASE_KEY_PATH in .env and add your service account JSON.')

def get_db():
    return db
