import requests
import re
import time

class BingScraper:
    def scrape_bing_images(self, url):
        # هيدر لتمويه بينغ بأننا متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            # استراحة بسيطة عشان ما نكشف كـ "بوت"
            time.sleep(2) 
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # هذا النمط (Regex) بيبحث داخل كود الصفحة عن الروابط الأصلية للصور
                # اللي بتنتهي بـ jpg أو png أو jpeg
                links = re.findall(r'murl&quot;:&quot;(http.*?\.jpg|http.*?\.png|http.*?\.jpeg)', response.text)
                
                # رح نأخذ أول 6 صور بس مثل ما طلبت
                return links[:6]
        except Exception as e:
            print(f"❌ فشل السحب من الرابط: {e}")
            
        return []
