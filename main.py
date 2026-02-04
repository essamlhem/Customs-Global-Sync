import os
import requests
import pandas as pd
from Scraper import SupabaseScraper
from Processor import DataProcessor

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def main():
    try:
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        
        processor = DataProcessor()
        df = processor.process_data(raw_data)
        
        # فحص مطابقة الصور: هل كل صف له رابط؟
        total_rows = len(df)
        rows_with_images = df[df['image_search_link'] != ""].shape[0]
        missing_images = total_rows - rows_with_images
        
        # حفظ الملف المحدث
        df.to_excel("Across_MENA_Images_Check.xlsx", index=False)
        df.to_json('knowledge_base.json', orient='records', force_ascii=False)

        # رسالة التقرير المركز على الصور
        report = (
            f"🖼️ **تقرير مطابقة الصور الذكي**\n\n"
            f"✅ إجمالي الصفوف: `{total_rows}`\n"
            f"🔗 صفوف بروابط صور: `{rows_with_images}`\n"
            f"⚠️ صفوف مفقودة الصور: `{missing_images}`\n\n"
            f"📌 تم تحسين كلمات البحث لضمان دقة أعلى في النتائج المرفقة في ملف الإكسل."
        )
        
        # إرسال التقرير مع الملف
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open("Across_MENA_Images_Check.xlsx", 'rb') as f:
            requests.post(url, data={'chat_id': CHAT_ID, 'caption': report, 'parse_mode': 'Markdown'}, files={'document': f})

    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': f"❌ خطأ: {str(e)}"})

if __name__ == "__main__":
    main()
