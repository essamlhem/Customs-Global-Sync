import requests
import re
import time
import random

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) Chrome/119.0.0.0 Safari/537.36'
        ]

    def get_real_images(self, brand, model):
        query = f"{brand} {model}".replace("nan", "").strip()
        if len(query) < 3: return []

        # المحاولة الأولى من Bing (أكثر استقراراً حالياً)
        try:
            time.sleep(random.uniform(2.0, 4.5)) # تأخير بشري
            url = f"https://www.bing.com/images/search?q={query}&safeSearch=Moderate"
            headers = {'User-Agent': random.choice(self.agents)}
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                links = re.findall(r'murl&quot;:&quot;(http[^&;]+?\.(?:jpg|png|jpeg|webp))', response.text)
                if len(links) >= 6:
                    print(f"✅ Bing: لقطنا 6 صور لـ {query}")
                    return links[:6]
        except:
            pass

        # محاولة ثانية من DuckDuckGo إذا فشل Bing
        try:
            url = f"https://duckduckgo.com/i.js?q={query}&o=json&v=1"
            response = self.session.get(url, headers={'User-Agent': random.choice(self.agents)}, timeout=15)
            if response.status_code == 200:
                results = response.json().get('results', [])
                links = [r.get('image') for r in results if r.get('image')][:6]
                if links:
                    print(f"✅ DuckDuckGo: لقطنا {len(links)} صور لـ {query}")
                    return links
        except:
            pass

        return []
