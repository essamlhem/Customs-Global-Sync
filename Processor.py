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

    @staticmethod
    def get_direct_image_url(description):
        # توليد كلمة مفتاحية للبحث عن صورة
        search_term = description.split(',')[0].replace(' ', ',')
        return f"https://source.unsplash.com/featured/?{search_term}"

    @staticmethod
    def generate_global_link(hs_code):
        if not hs_code: return ""
        # هذا الرابط سيعمل الموديل على "زيارته" لاحقاً لجلب الداتا
        return f"https://globaltradehelpdesk.org/ar/resources/search-hs-code?code={hs_code}"

    def process_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        df['hs_code'] = df['material'].apply(self.extract_hs_code)
        df['description_clean'] = df['material'].apply(self.clean_description)
        df['image_url'] = df['description_clean'].apply(self.get_direct_image_url)
        
        # ربط كل سجل بمرجعه العالمي للموديل
        df['ai_reference_link'] = df['hs_code'].apply(self.generate_global_link)
        
        return df
