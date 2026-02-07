import requests
import json

class SupabaseScraper:
    def __init__(self):
        # البيانات اللي أنت استخرجتها من الـ Network
        self.url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
        self.headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"
        }

    def fetch_all_data(self):
        try:
            print("📡 جاري سحب البيانات من Supabase...")
            response = requests.get(self.url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ تم سحب {len(data)} سجل بنجاح.")
                return data
            else:
                print(f"❌ فشل السحب. كود الخطأ: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ حدث خطأ تقني: {e}")
            return None
