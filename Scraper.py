import requests
import random
import time

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()
        # قائمة متصفحات وهمية للتنويع وتجنب الحظر
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def get_real_images(self, brand, model):
        query = f"{brand} {model}".strip()
        if not query or query == "nan nan":
            return []
            
        # استخدام رابط البحث التقليدي المباشر
        search_url = "https://duckduckgo.com/i.js"
        params = {
            'q': query,
            'o': 'json',
            'p': '1',
            'vqd': '', # سيتم تجاهله أو طلبه لاحقاً
            'f': ',,,',
            'exit': '1'
        }
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://duckduckgo.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }

        try:
            # إضافة تأخير بسيط جداً بين الطلبات لتجنب الحظر
            time.sleep(random.uniform(1.5, 3.0)) 
            
            response = self.session.get(search_url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                # سحب الروابط وتصفيتها
                images = [r.get('image') for r in results if r.get('image')][:5]
                if images:
                    print(f"✅ لقطنا {len(images)} صور لـ: {query}")
                return images
            else:
                print(f"⚠️ الموقع رفض الطلب (كود {response.status_code})")
        except Exception as e:
            print(f"❌ خطأ في فك تشفير البيانات: {e}")
            
        return []
