import re
import pandas as pd

class DataProcessor:
    @staticmethod
    def clean_description(text):
        if not text: return ""
        # حذف الأرقام والأقواس والرموز ليبقى الوصف نظيفاً للذكاء الاصطناعي
        clean = re.sub(r'\[.*?\]|\(.*?\)|\d+', '', text)
        return clean.strip().replace('  ', ' ')

    @staticmethod
    def extract_hs_code(text):
        if not text: return ""
        # استخراج رقم البند الجمركي فقط
        match = re.search(r'\d{4,}', text)
        return match.group(0) if match else ""

    def process_data(self, raw_data):
        df = pd.DataFrame(raw_data)
        df['hs_code'] = df['material'].apply(self.extract_hs_code)
        df['description_clean'] = df['material'].apply(self.clean_description)
        # هنا يمكننا إضافة أي منطق مستقبلي للذكاء الاصطناعي
        return df
