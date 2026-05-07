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
    def create_agent(listing_id, listing_type, listing_data):
        if listing_type == 'home':
            prompt = (
                f"You are a helpful assistant for Air (AI Reservations). "
                f"The listing is '{listing_data['title']}' in {listing_data.get('location', {}).get('city', '')}. "
                f"Price: ${listing_data.get('price', 0)}/night. "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests with questions and bookings."
            )
        elif listing_type == 'experience':
            prompt = (
                f"You are an enthusiastic guide for an Air experience: '{listing_data['title']}'. "
                f"Price: ${listing_data.get('price', 0)}. "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests learn about and book this experience."
            )
        else:
            prompt = (
                f"You are a helpful assistant for the Air event '{listing_data['title']}'. "
                f"Description: {listing_data.get('description', '')}. "
                f"Help guests with ticketing questions."
            )

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
