import requests
import re
import time
import random

class SupabaseScraper:
    def __init__(self):
        self.session = requests.Session()

    def get_real_images(self, brand, model):
        query = f"{brand} {model} item photo".replace("nan", "").strip()
        if not query or len(query) < 3: return []

        print(f"📡 محاولة قنص صور لـ: {query}")
        
        # مصفوفة روابط لمحركات بحث مختلفة لضمان النتيجة
        search_urls = [
            f"https://www.google.com/search?q={query}&tbm=isch&asearch=ichunk&async=_id:rg_s,_pms:s,_fmt:pc",
            f"https://www.bing.com/images/search?q={query}&first=1"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        try:
            # نختار محرك بحث عشوائي كل مرة
            url = random.choice(search_urls)
            time.sleep(random.uniform(3, 5)) # تأخير ضروري جداً
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # استخراج الروابط باستخدام Regex يبحث عن روابط الصور الحقيقية
                # هذا النمط يبحث عن الروابط التي تنتهي بامتدادات الصور داخل كود الصفحة
                image_links = re.findall(r'(https?://[^\s"\';<>]+?\.(?:jpg|jpeg|png|webp))', response.text)
                
                # تصفية الروابط لاستبعاد الصور الصغيرة (icons/logos)
                clean_links = [link for link in image_links if "google" not in link and "bing" not in link and "gstatic" not in link]
                
                if len(clean_links) >= 1:
                    final_images = clean_links[:6]
                    print(f"✅ مبروك! لقطنا {len(final_images)} صور حقيقية.")
                    return final_images
                
            print(f"⚠️ المحرك أعاد صفحة لكن بدون روابط مباشرة لـ {query}")
        except Exception as e:
            print(f"❌ خطأ في القنص: {e}")
            
        return []
