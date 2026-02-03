import requests
import os

class SupabaseScraper:
    def __init__(self):
        self.api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def fetch_raw_data(self):
        headers = {'apikey': self.key.strip(), 'Authorization': f'Bearer {self.key.strip()}'}
        response = requests.get(self.api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch data: {response.status_code}")
