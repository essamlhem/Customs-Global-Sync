import requests
import random
import time

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()
        # متصفحات متنوعة للتمويه
        self.agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) Chrome/119.0.0.0 Safari/537.36'
        ]

    def get_real_images(self, brand, model):
        # تنظيف كلمة البحث
        query = f"{brand} {model}".replace("nan", "").strip()
        if len(query) < 3: return []

        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1', 'f': ',,,', 'p': '1'}
        headers = {
            'User-Agent': random.choice(self.agents),
            'Referer': 'https://duckduckgo.com/'
        }

        try:
            # إضافة تأخير بسيط (ثانية واحدة) لتجنب الحظر
            time.sleep(random.uniform(1.0, 2.0))
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                # جلب روابط الصور الحقيقية
                images = [r.get('image') for r in results if r.get('image')][:5]
                if images:
                    print(f"✅ تم العثور على {len(images)} صور لـ: {query}")
                return images
            else:
                print(f"⚠️ تنبيه: حظر مؤقت من محرك البحث (Status: {response.status_code})")
        except:
            pass
            
        return []
