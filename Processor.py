import re
import pandas as pd
import urllib.parse

class DataProcessor:
    @staticmethod
    def clean_for_search(text):
        if not text: return ""
        # إزالة الرموز والكلمات التي لا تهم محرك البحث عن الصور
        clean = re.sub(r'\[.*?\]|\(.*?\)|\d+|/|-', '', text)
        # إزالة كلمات جمركية متكررة قد تشوش البحث
        exclude_words = ['بند', 'تعريفة', 'رسوم', 'كيلو', 'كغ', 'طن']
        words = clean.split()
        filtered_words = [w for w in words if w not in exclude_words]
        return " ".join(filtered_words).strip()

    @staticmethod
    def get_stable_image_url(description):
        if not description: return ""
        # استخدام الاسم المنظف للبحث
        query = DataProcessor.clean_for_search(description)
        if not query: return ""
        encoded_query = urllib.parse.quote(query)
        # رابط مباشر لنتائج صور Bing
        return f"https://www.bing.com/images/search?q={encoded_query}"

    def process_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        # استخراج الـ HS Code
        df['hs_code'] = df['material'].apply(lambda x: re.search(r'\d{4,}', str(x)).group(0) if re.search(r'\d{4,}', str(x)) else "")
        # تنظيف الوصف للعرض
        df['description_clean'] = df['material'].apply(lambda x: re.sub(r'\[.*?\]|\d+', '', str(x)).strip())
        # توليد روابط الصور بناءً على الوصف المنظف للبحث
        df['image_search_link'] = df['material'].apply(self.get_stable_image_url)
        
        # تصنيف تلقائي بسيط
        df['category'] = df['hs_code'].apply(self.classify_category)
        return df

    @staticmethod
    def classify_category(hs_code):
        if not hs_code: return "أخرى"
        chapter = hs_code[:2]
        categories = {"01": "حيوانات", "07": "خضروات", "61": "ملابس", "84": "آلات"}
        return categories.get(chapter, "تصنيف عام")
