import requests

class SupabaseScraper:
    def __init__(self):
        # الرابط المباشر
        self.api_url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=id,brand,model,hs_code"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"

    def fetch_raw_data(self):
        """جلب البيانات الأساسية فقط لتقليل استهلاك الـ Egress Quota"""
        headers = {
            'apikey': self.key.strip(), 
            'Authorization': f'Bearer {self.key.strip()}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ تم جلب {len(data)} مادة بنجاح")
                return data
            else:
                print(f"❌ خطأ سوبابيس {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"⚠️ فشل الاتصال: {e}")
            return []

    def get_real_images(self, brand, model):
        """دالة الصور الذكية"""
        query = f"{brand} {model} watch"
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                links = [r.get('image') for r in results if r.get('image') and any(r.get('image').lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])]
                return links[:6]
        except: pass
        return []
