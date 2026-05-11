import requests
import os

class RetellAIService:
    BASE_URL = os.getenv('RETELL_API_BASE_URL', 'https://api.retellai.com')
    API_KEY = os.getenv('RETELL_API_KEY', '')

    @staticmethod
    def _headers():
        return {
            'Authorization': f'Bearer {RetellAIService.API_KEY}',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _build_prompt(listing_id, listing_type, listing_data):
        source_note = ' (sourced from Google Places)' if listing_data.get('source') == 'google_places' else ''
        location = listing_data.get('location', {})
        city = location.get('city', '') if isinstance(location, dict) else ''
        amenities = listing_data.get('amenities', [])
        amenity_text = f" Amenities include: {', '.join(amenities)}." if amenities else ''

        if listing_type == 'home':
            return (
                f"You are a friendly voice assistant for Air (AI Reservations){source_note}. "
                f"You are answering calls about the property '{listing_data.get('title', 'this listing')}' "
                f"located in {city}. "
                f"Price: ${listing_data.get('price', 0)}/night. "
                f"Bedrooms: {listing_data.get('bedrooms', 'N/A')}, "
                f"Bathrooms: {listing_data.get('bathrooms', 'N/A')}.{amenity_text} "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests with questions about availability, amenities, local tips, and bookings. "
                f"Be warm, concise, and helpful."
            )
        elif listing_type == 'experience':
            return (
                f"You are an enthusiastic voice assistant for an Air experience{source_note}: "
                f"'{listing_data.get('title', 'this experience')}'. "
                f"Price: ${listing_data.get('price', 0)} per person. "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests learn about and book this experience. Be energetic and informative."
            )
        else:
            return (
                f"You are a helpful voice assistant for the Air event "
                f"'{listing_data.get('title', 'this event')}'{source_note}. "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests with ticketing questions. Be helpful and friendly."
            )

    @staticmethod
    def create_agent(listing_id, listing_type, listing_data):
        prompt = RetellAIService._build_prompt(listing_id, listing_type, listing_data)
        payload = {
            'agent_name': f'air_{listing_type}_{listing_id}',
            'language': 'en',
            'system_prompt': prompt,
            'llm_model': 'gpt-4',
        }
        try:
            r = requests.post(
                f'{RetellAIService.BASE_URL}/v1/create-agent',
                json=payload, headers=RetellAIService._headers(), timeout=10
            )
            return r.json().get('agent_id') if r.status_code == 201 else None
        except Exception as e:
            print(f'Retell create_agent error: {e}')
            return None

    @staticmethod
    def get_or_create_agent(listing_id, listing_type, listing_data):
        """Return existing agent ID or create a new one and persist it to Firestore."""
        existing_id = (listing_data.get('aiConfig') or {}).get('agentId', '')
        if existing_id:
            return existing_id

        if not RetellAIService.API_KEY:
            return None

        agent_id = RetellAIService.create_agent(listing_id, listing_type, listing_data)
        if agent_id:
            try:
                from app.firebase_config import db
                collection = {'home': 'homes', 'experience': 'experiences', 'party': 'parties'}.get(listing_type, 'homes')
                if db:
                    db.collection(collection).document(listing_id).update({
                        'aiConfig': {'enabled': True, 'agentId': agent_id}
                    })
            except Exception as e:
                print(f'Failed to persist agent ID: {e}')
        return agent_id

    @staticmethod
    def create_call_token(agent_id, user_id, listing_id):
        payload = {
            'agent_id': agent_id,
            'user_id': user_id,
            'metadata': {'listing_id': listing_id}
        }
        try:
            r = requests.post(
                f'{RetellAIService.BASE_URL}/v1/create-call-token',
                json=payload, headers=RetellAIService._headers(), timeout=10
            )
            return r.json().get('access_token') if r.status_code == 200 else None
        except Exception as e:
            print(f'Retell create_call_token error: {e}')
            return None
