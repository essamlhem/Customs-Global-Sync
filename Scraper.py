import requests
import json

class SupabaseScraper:
    def get_real_images(self, brand, model):
        # البحث بكلمات عامة لضمان النتائج لكل أنواع السلع
        query = f"{brand} {model}"
        search_url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://duckduckgo.com/'
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=15)
            if response.status_code == 200:
                results = response.json().get('results', [])
                image_urls = [r.get('image') for r in results if r.get('image') and 
                              any(ext in r.get('image').lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
                return image_urls[:5] # نأخذ أول 5 صور
        except Exception as e:
            print(f"⚠️ خطأ في السحب لـ {query}: {e}")
        
        return []
