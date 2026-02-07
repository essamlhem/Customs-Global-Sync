from duckduckgo_search import DDGS
import time
import random

class SupabaseScraper:
    def get_real_images(self, brand, model):
        query = f"{brand} {model}".replace("nan", "").strip()
        if not query or len(query) < 3:
            return []

        print(f"📡 محاولة صيد احترافية (DDGS) لـ: {query}")
        
        try:
            # تأخير عشوائي بسيط لضمان عدم الحظر
            time.sleep(random.uniform(2, 4))
            
            with DDGS() as ddgs:
                # طلب 6 صور مباشرة
                results = list(ddgs.images(
                    query,
                    region="wt-wt",
                    safesearch="moderate",
                    max_results=6
                ))
                
                if results:
                    image_urls = [r.get('image') for r in results]
                    print(f"✅ لقطنا {len(image_urls)} صور حقيقية!")
                    return image_urls
                else:
                    print(f"⚠️ لم يتم العثور على نتائج.")
        
        except Exception as e:
            print(f"❌ خطأ في المكتبة: {e}")
            # إذا صار ضغط، انتظر شوي
            time.sleep(5)
            
        return []
