import requests

class SupabaseScraper:
    def get_real_images(self, brand, model):
        query = f"{brand} {model} watch"
        search_url = "https://duckduckgo.com/i.js"
        params = {'q': query, 'o': 'json', 'v': '1'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json().get('results', [])
                # تصفية الروابط للحصول على الصور فقط
                return [r.get('image') for r in results if r.get('image') and 
                        any(r.get('image').lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])][:6]
        except:
            pass
        return []
