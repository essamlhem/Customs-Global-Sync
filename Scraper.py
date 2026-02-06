import requests
import os

class SupabaseScraper:
    def __init__(self):
        # الرابط الأساسي بدون الـ parameters
        self.base_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def fetch_raw_data_batched(self, offset=0, limit=500):
        """جلب البيانات من سوبابيس على دفعات لتجنب خطأ الـ 402"""
        headers = {
            'apikey': self.key.strip(), 
            'Authorization': f'Bearer {self.key.strip()}',
            'Range': f'{offset}-{offset + limit - 1}' # ميزة سوبابيس لجلب نطاق معين
        }
        # نطلب البيانات مرتبة حسب الـ id عشان ما يتكرر شي
        url = f"{self.base_url}?select=%2A&order=id.asc"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 206: # 206 تعني Partial Content وهي طبيعية هنا
            return response.json()
        else:
            print(f"⚠️ فشل جلب الدفعة: {response.status_code}")
            return []

    def get_real_images(self, brand, model):
        """نفس دالة جلب الـ 6 صور اللي عملناها"""
        query = f"{brand} {model} watch"
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                links = [r.get('image') for r in results if r.get('image') and any(r.get('image').lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
                return links[:6]
        except: pass
        return []
