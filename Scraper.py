import requests
import random
import time
import re

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()
        # قائمة متصفحات حديثة جداً لتبدو كأنها طلبات حقيقية
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]

    def get_real_images(self, brand, model):
        # تنظيف الكلمات وحذف أي قيم فارغة أو غير مفهومة
        query = f"{brand} {model}".replace("nan", "").strip()
        if not query or len(query) < 3:
            return []

        print(f"📡 محاولة قنص صور لـ: {query}")
        
        # استخدام محرك بحث بديل (Bing) بأسلوب مباشر أو DuckDuckGo المحدث
        search_url = f"https://duckduckgo.com/i.js?q={query}&o=json&v=1&f=,,,&p=1"
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://duckduckgo.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }

        try:
            # إضافة تأخير عشوائي بشري (بين 2 إلى 4 ثوانٍ)
            # هذا السر في منع ظهور القوائم الفارغة
            time.sleep(random.uniform(2.0, 4.0))
            
            response = self.session.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results = data.get('results', [])
                    
                    # استخراج روابط الصور
                    image_urls = []
                    for r in results:
                        img = r.get('image')
                        if img and any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            image_urls.append(img)
                    
                    if image_urls:
                        print(f"✅ تم العثور على {len(image_urls[:5])} صور.")
                        return image_urls[:5]
                    else:
                        print(f"⚠️ الموقع أعاد نتائج ولكن بدون روابط صور.")
                except Exception as e:
                    print(f"❌ خطأ في تحليل JSON: {e}")
            elif response.status_code == 403:
                print("🚫 حظر (403): الموقع كشف السكريبت، يحتاج لتأخير أطول.")
            else:
                print(f"🛑 استجابة غير متوقعة: {response.status_code}")
                
        except Exception as e:
            print(f"❌ فشل الاتصال: {e}")
        
        return []
