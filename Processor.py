import re
import pandas as pd
import urllib.parse

class DataProcessor:
    @staticmethod
    def clean_description(text):
        if not text: return ""
        # حذف الأرقام والرموز ليكون البحث دقيق
        clean = re.sub(r'\[.*?\]|\(.*?\)|\d+', '', text)
        return clean.strip().replace('  ', ' ')

    @staticmethod
    def extract_hs_code(text):
        if not text: return ""
        match = re.search(r'\d{4,}', text)
        return match.group(0) if match else ""

    @staticmethod
    def get_stable_image_url(description):
        if not description: return "https://via.placeholder.com/150"
        
        # تحويل الوصف لكلمات مفتاحية بسيطة
        keywords = description.split(',')[0].replace(' ', ',')
        # استخدام محرك Pixabay أو نظام بحث صور مستقر
        # للتبسيط وضمان العمل، سنستخدم رابط بحث صور "Bing" المباشر لأنه يفتح دائماً
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
        
        # الرابط الجديد المستقر
        df['image_search_link'] = df['description_clean'].apply(self.get_stable_image_url)
        df['ai_reference_link'] = df['hs_code'].apply(self.generate_global_link)
        
        return df
