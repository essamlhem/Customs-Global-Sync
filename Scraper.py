import requests
import re
import json
import time

class SupabaseScraper:
    def get_real_images(self, brand, model):
        # الكود بضيف "Product" بدل "watch" عشان يكون عام لكل أنواع بضاعتك
        query = f"{brand} {model}"
        print(f"📡 جاري البحث عن: {query}...")
        
        # استخدام محرك بحث بديل وأكثر مرونة للسكربتات
        search_url = f"https://duckduckgo.com/pd.js?q={query}&kl=wt-wt"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://duckduckgo.com/'
        }

        try:
            # محاولة جلب البيانات مع مهلة زمنية
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                image_urls = []
                for r in results:
                    img_url = r.get('image')
                    if img_url:
                        # التأكد من أن الرابط ينتهي بصيغة صورة أو يحتوي عليها
                        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            image_urls.append(img_url)
                
                # نأخذ أول 5 صور فقط لتقليل الحجم
                final_images = image_urls[:5]
                if final_images:
                    print(f"✅ تم العثور على {len(final_images)} صور لـ {brand}")
                else:
                    print(f"⚠️ لم يتم العثور على صور مباشرة لـ {brand}")
                
                return final_images
                
            elif response.status_code == 403:
                print("🚫 تم حظر الطلب (403) - الموقع كشف السكريبت")
            else:
                print(f"🛑 خطأ من المصدر: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطأ تقني في السحب: {e}")
        
        return []
