import requests
import re
import time
import random
from duckduckgo_search import DDGS

class SupabaseScraper:
    def get_real_images(self, brand, model):
        # إضافة كلمات دلالية تجارية لضمان دقة الصور
        query = f"{brand} {model} product listing gallery".replace("nan", "").strip()
        if not query or len(query) < 3: return []

        print(f"🎯 قنص تجاري دقيق لـ: {query}")
        
        try:
            time.sleep(random.uniform(3, 5))
            with DDGS() as ddgs:
                # نطلب من DuckDuckGo صور من مواقع التسوق فقط
                results = list(ddgs.images(
                    query,
                    region="wt-wt",
                    safesearch="off", # أحياناً الموديلات التقنية تحتاج فلاتر مفتوحة
                    max_results=15 # نطلب عدد أكبر لنختار الأفضل
                ))
                
                if results:
                    final_urls = []
                    for r in results:
                        img_url = r.get('image', '')
                        # استبعاد روابط يوتيوب وأي روابط غير موثوقة
                        if any(x in img_url.lower() for x in ['ytimg', 'youtube', 'facebook', 'instagram', 'thumbnail']):
                            continue
                        
                        final_urls.append(img_url)
                        if len(final_urls) == 6: break
                    
                    if final_urls:
                        print(f"✅ تم إيجاد {len(final_urls)} صور تجارية نظيفة.")
                        return final_urls
                        
        except Exception as e:
            print(f"⚠️ فشل القنص: {e}")
            
        return []
