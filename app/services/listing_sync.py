"""
Thin fire-and-forget wrapper that keeps Retell knowledge bases in sync
whenever listings are created, updated, or deleted in Firestore.

A Retell outage or misconfiguration never blocks listing CRUD —
every call is wrapped in try/except and failures are logged to the
`kb_sync_failures` Firestore collection for later inspection.
"""

from app.services.retell_kb_service import RetellKBService


def sync_listing(listing_type: str, listing_id: str, action: str, listing_data: dict | None = None):
    """
    listing_type : 'home' | 'experience' | 'party'
    listing_id   : Firestore document ID
    action       : 'create' | 'update' | 'delete'
    listing_data : the current document dict (required for create/update)
    """
    try:
        if action == 'create':
            if listing_data:
                RetellKBService.add_listing(listing_type, listing_id, listing_data)

        elif action == 'update':
            if listing_data:
                RetellKBService.update_listing(listing_type, listing_id, listing_data)

        elif action == 'delete':
            source_id = (listing_data or {}).get('retellSourceId', '')
            RetellKBService.remove_listing(listing_type, listing_id, source_id)

    except Exception as e:
        print(f'[ListingSync] {action} {listing_type}/{listing_id} failed: {e}')
        _log_failure(listing_type, listing_id, action, str(e))


def _log_failure(listing_type, listing_id, action, error_msg):
    try:
        from app.firebase_config import db
        from firebase_admin import firestore as fs
        if db:
            db.collection('kb_sync_failures').add({
                'listingType': listing_type,
                'listingId': listing_id,
                'action': action,
                'error': error_msg,
                'created_at': fs.SERVER_TIMESTAMP,
            })
    except Exception:
        pass  # if logging fails too, just drop it
