import re
import pandas as pd
import urllib.parse

class DataProcessor:
    @staticmethod
    def clean_for_search(text):
        if not text: return ""
        # إزالة الأقواس وما بداخلها، والأرقام، والشرطات
        clean = re.sub(r'\[.*?\]|\(.*?\)|\d+|/|-', '', str(text))
        # كلمات جمركية وتقنية بتخرب نتائج الصور، رح نشيلها من البحث فقط
        exclude_words = ['بند', 'تعريفة', 'رسوم', 'كيلو', 'كغ', 'طن', 'مادة', 'نوع']
        words = clean.split()
        filtered_words = [w for w in words if w not in exclude_words and len(w) > 1]
        return " ".join(filtered_words).strip()

    @staticmethod
    def get_stable_image_url(description):
        query = DataProcessor.clean_for_search(description)
        if not query: return ""
        encoded_query = urllib.parse.quote(query)
        # رابط مباشر لنتائج صور Bing لضمان المطابقة
        return f"https://www.bing.com/images/search?q={encoded_query}"

    def process_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        # استخراج HS Code
        df['hs_code'] = df['material'].apply(lambda x: re.search(r'\d{4,}', str(x)).group(0) if re.search(r'\d{4,}', str(x)) else "")
        # تنظيف الوصف للعرض في الإكسل
        df['description_clean'] = df['material'].apply(lambda x: re.sub(r'\[.*?\]|\d+', '', str(x)).strip())
        # توليد رابط الصورة الذكي
        df['image_search_link'] = df['material'].apply(self.get_stable_image_url)
        return df
