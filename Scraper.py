import requests
import re
import time
import random

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()
        # متصفحات متنوعة لضمان عدم الحظر
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

    def get_real_images(self, brand, model):
        # تجهيز كلمة البحث
        search_query = f"{brand} {model}".replace("nan", "").strip()
        if not search_query or len(search_query) < 3:
            return []

        # البحث في Bing Images
        url = f"https://www.bing.com/images/search?q={search_query}&safeSearch=Moderate"
        
        try:
            # تأخير بشري بسيط لضمان استمرار السحب بدون حظر
            time.sleep(random.uniform(1.5, 2.5))
            
            response = self.session.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                # استخراج روابط الصور الأصلية باستخدام التعبيرات النمطية
                # الكود يبحث عن الرابط المباشر للصورة (murl)
                image_links = re.findall(r'murl&quot;:&quot;(http[^&;]+?\.(?:jpg|png|jpeg|webp))', response.text)
                
                if image_links:
                    # نأخذ أول 6 صور كما طلبت يا عيسى
                    final_links = image_links[:6]
                    print(f"✅ تم صيد {len(final_links)} صور لـ: {search_query}")
                    return final_links
                else:
                    print(f"⚠️ لم نجد صوراً لـ: {search_query} - سنحاول في المرة القادمة")
            else:
                print(f"🛑 Bing رفض الطلب، كود الخطأ: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطأ تقني أثناء الصيد: {e}")
            
        return []
