import requests
import pandas as pd

class SupabaseScraper:
    def __init__(self):
        # الرابط والمفتاح اللي استخرجتهم أنت
        self.url = "https://xlugavhmvnmagaxtcdxy.supabase.co/rest/v1/bands?select=%2A"
        self.headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhsdWdhdmhtdm5tYWdheHRjZHh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2ODkyNzQsImV4cCI6MjA1NTI2NTI3NH0.mCJzpoVbvGbkEwLPyaPcMZJGdaSOwaSEtav85rK-dWA"
        }

    def fetch_all_as_dataframe(self):
        try:
            print("📡 جاري الاتصال بـ Supabase...")
            response = requests.get(self.url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                return df
            else:
                print(f"❌ خطأ في السحب: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ حدث خطأ تقني: {e}")
            return None
