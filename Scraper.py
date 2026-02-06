import requests

class SupabaseScraper:
    def __init__(self):
        # الرابط المباشر لجلب كافة البيانات دفعة واحدة
        self.api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=*"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def fetch_raw_data(self):
        """جلب كل البيانات بطلبة واحدة لتفادي مشاكل الـ 402 والـ Offsets"""
        headers = {
            'apikey': self.key.strip(), 
            'Authorization': f'Bearer {self.key.strip()}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ تم جلب {len(data)} مادة من Supabase")
                return data
            else:
                print(f"❌ خطأ {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"⚠️ فشل الاتصال بسوبابيس: {e}")
            return []

    def get_real_images(self, brand, model):
        """البحث عن 6 صور حقيقية للمنتج"""
        query = f"{brand} {model} watch"
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                links = []
                for r in results:
                    img = r.get('image')
                    if img and any(img.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        links.append(img)
                    if len(links) == 6: break
                return links
        except: pass
        return []
