import requests
import os

class SupabaseScraper:
    def __init__(self):
        # الرابط والمفتاح الخاص بك كما هما
        self.api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def get_real_images(self, brand, model):
        """دالة ذكية لجلب 6 روابط صور حقيقية من محرك البحث"""
        query = f"{brand} {model} watch"
        # نستخدم DuckDuckGo للحصول على نتائج سريعة ومباشرة
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                image_links = []
                for r in results:
                    img_url = r.get('image')
                    # التأكد من أن الرابط لصورة حقيقية
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        image_links.append(img_url)
                    if len(image_links) == 6:
                        break
                
                # احتياط في حال لم يجد صوراً مباشرة
                if not image_links:
                    image_links = [f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch"]
                return image_links
        except:
            return []
        return []

    def fetch_raw_data(self):
        """جلب البيانات باستخدام مفاتيحك الأصلية"""
        headers = {
            'apikey': self.key.strip(), 
            'Authorization': f'Bearer {self.key.strip()}'
        }
        response = requests.get(self.api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch data: {response.status_code}")
