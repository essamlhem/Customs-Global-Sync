import requests

class SupabaseScraper:
    def __init__(self):
        self.api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=*"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def fetch_raw_data(self):
        headers = {
            'apikey': self.key.strip(), 
            'Authorization': f'Bearer {self.key.strip()}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(self.api_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def get_real_images(self, brand, model):
        query = f"{brand} {model} watch"
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                return [r.get('image') for r in results if r.get('image') and any(r.get('image').lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])][:6]
        except: pass
        return []
