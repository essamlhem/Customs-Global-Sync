import re
import pandas as pd
import urllib.parse

class DataProcessor:
    @staticmethod
    def clean_description(text):
        if not text: return ""
        clean = re.sub(r'\[.*?\]|\(.*?\)|\d+', '', text)
        return clean.strip().replace('  ', ' ')

    @staticmethod
    def extract_hs_code(text):
        if not text: return ""
        match = re.search(r'\d{4,}', text)
        return match.group(0) if match else ""

    # --- الميزة الجديدة: المصنف الذكي ---
    @staticmethod
    def classify_category(hs_code):
        if not hs_code or len(hs_code) < 2: return "أخرى"
        
        # استخراج أول رقمين لتحديد القسم الكبير
        chapter = hs_code[:2]
        
        categories = {
            "01": "حيوانات حية", "02": "لحوم", "07": "خضروات", "08": "فواكه",
            "61": "ألبسة وتريكو", "62": "ألبسة جاهزة", "64": "أحذية",
            "84": "آلات ومعدات", "85": "أجهزة كهربائية", "87": "سيارات وقطعها",
            "94": "أثاث ومفروشات"
        }
        return categories.get(chapter, "تصنيف عام جمركي")

    @staticmethod
    def get_stable_image_url(description):
        if not description: return ""
        query = urllib.parse.quote(description)
        return f"https://www.bing.com/images/search?q={query}"

    @staticmethod
    def generate_global_link(hs_code):
        if not hs_code: return ""
        return f"https://globaltradehelpdesk.org/ar/resources/search-hs-code?code={hs_code}"

    def process_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        df['hs_code'] = df['material'].apply(self.extract_hs_code)
        df['description_clean'] = df['material'].apply(self.clean_description)
        
        # إضافة التصنيف الذكي بناءً على رقم البند
        df['category'] = df['hs_code'].apply(self.classify_category)
        
        df['image_search_link'] = df['description_clean'].apply(self.get_stable_image_url)
        df['ai_reference_link'] = df['hs_code'].apply(self.generate_global_link)
        
        return df
