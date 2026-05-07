from werkzeug.utils import secure_filename
import os

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

class StorageService:

    @staticmethod
    def upload(file, folder):
        if not file or file.filename == '':
            return None
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED:
            return None
        try:
            from app.firebase_config import bucket
            if not bucket:
                return None
            filename = secure_filename(file.filename)
            blob = bucket.blob(f"{folder}/{filename}")
            blob.upload_from_string(file.read(), content_type=file.content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f'Upload error: {e}')
            return None

    @staticmethod
    def upload_multiple(files, folder):
        urls = []
        for f in files:
            url = StorageService.upload(f, folder)
            if url:
                urls.append(url)
        return urls
