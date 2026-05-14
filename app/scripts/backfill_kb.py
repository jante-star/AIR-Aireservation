"""
One-shot backfill script: walks every published listing in Firestore
and adds it as a text source in the matching Retell knowledge base.

Run once after you have created the three KBs in the Retell dashboard
and filled in the corresponding env vars (RETELL_KB_*_ID).

Usage:
    python -m app.scripts.backfill_kb
"""

import sys
import os

# Ensure the project root is on the path when run as `python -m app.scripts.backfill_kb`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

from app.firebase_config import db
from app.services.retell_kb_service import RetellKBService, KB_IDS


def backfill(collection, listing_type, status_filter='published'):
    if not db:
        print('  ✗ Firebase not connected — check FIREBASE_KEY_PATH')
        return 0, 0

    kb_id = KB_IDS.get(listing_type)
    if not kb_id:
        print(f'  ✗ RETELL_KB_{listing_type.upper()}S_ID not set — skipping')
        return 0, 0

    query = db.collection(collection)
    if status_filter:
        query = query.where('status', '==', status_filter)

    docs = list(query.stream())
    ok = fail = 0

    for doc in docs:
        data = doc.to_dict()
        listing_id = data.get('id', doc.id)

        # Skip listings already synced (have a retellSourceId)
        if data.get('retellSourceId'):
            print(f'  ↷ {data.get("title", listing_id)[:50]} — already synced, skipping')
            ok += 1
            continue

        source_id = RetellKBService.add_listing(listing_type, listing_id, data)
        if source_id:
            print(f'  ✓ {data.get("title", listing_id)[:50]}  →  source {source_id}')
            ok += 1
        else:
            print(f'  ✗ {data.get("title", listing_id)[:50]}  — failed')
            fail += 1

    return ok, fail


def main():
    print('\n═══ Air — Retell Knowledge Base Backfill ═══\n')

    total_ok = total_fail = 0

    print('▶ Homes (kb_homes)')
    ok, fail = backfill('homes', 'home', status_filter='published')
    print(f'  Done: {ok} synced, {fail} failed\n')
    total_ok += ok; total_fail += fail

    print('▶ Experiences (kb_experiences)')
    ok, fail = backfill('experiences', 'experience', status_filter='published')
    print(f'  Done: {ok} synced, {fail} failed\n')
    total_ok += ok; total_fail += fail

    print('▶ Events/Parties (kb_parties)')
    ok, fail = backfill('parties', 'party', status_filter='published')
    print(f'  Done: {ok} synced, {fail} failed\n')
    total_ok += ok; total_fail += fail

    print(f'═══ Complete: {total_ok} synced, {total_fail} failed ═══\n')
    if total_fail:
        print('Check kb_sync_failures in Firestore for details.')
    sys.exit(1 if total_fail else 0)


if __name__ == '__main__':
    main()
