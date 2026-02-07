import requests
import pandas as pd

class SupabaseScraper:
    def __init__(self):
        # الرابط والمفاتيح اللي استخرجتها من الـ Network
        self.url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
        self.headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"
        }

    def fetch_all_data(self):
        try:
            print("📡 جاري سحب البيانات من المصدر...")
            response = requests.get(self.url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data)
            else:
                print(f"❌ خطأ في الاتصال: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ حدث خطأ: {e}")
            return None
