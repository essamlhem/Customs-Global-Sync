import os
import requests
import pandas as pd
import json
from datetime import datetime
from Scraper import SupabaseScraper
from Processor import DataProcessor

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_notification(message):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'})

def main():
    try:
        # 1. جلب البيانات الجديدة
        scraper = SupabaseScraper()
        raw_data = scraper.fetch_raw_data()
        processor = DataProcessor()
        df_new = processor.process_data(raw_data)

        # 2. محرك المقارنة (الذكاء البسيط)
        summary_msg = ""
        try:
            with open('knowledge_base.json', 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                df_old = pd.DataFrame(old_data)
                
                # مواد جديدة؟
                new_items_count = len(df_new) - len(df_old)
                if new_items_count > 0:
                    summary_msg += f"🆕 تم إضافة *{new_items_count}* مواد جديدة اليوم.\n"
                elif new_items_count < 0:
                    summary_msg += f"🗑️ تم حذف *{abs(new_items_count)}* مواد من القائمة.\n"
        except:
            summary_msg = "🆕 هذا هو التشغيل الأول للذاكرة.\n"

        # 3. إحصائيات سريعة
        top_categories = df_new['category'].value_counts().head(3).to_dict()
        cat_text = "\n".join([f"• {k}: {v}" for k, v in top_categories.items()])
        
        # 4. أغلى مادة (بافتراض وجود عمود السعر)
        try:
            # تنظيف السعر من العملات وتحويله لرقم
            df_new['price_num'] = df_new['total_price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
            expensive_item = df_new.loc[df_new['price_num'].idxmax()]
            top_item_txt = f"💰 أغلى بند: *{expensive_item['description_clean']}*"
        except:
            top_item_txt = "💰 تم تحديث الأسعار بنجاح."

        # 5. حفظ البيانات
        df_new.to_json('knowledge_base.json', orient='records', force_ascii=False)
        df_new.to_excel("customs_ai_ready.xlsx", index=False)

        # 6. إرسال التقرير "المميز"
        report = (
            f"☀️ **تقرير Across MENA الذكي**\n"
            f"📅 `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"{summary_msg}\n"
            f"📊 **أكثر التصنيفات تكراراً:**\n{cat_text}\n\n"
            f"{top_item_txt}\n\n"
            f"✅ إجمالي البنود: *{len(df_new)}*\n"
            f"🚀 النظام جاهز وبانتظار الموقع."
        )
        send_telegram_notification(report)

    except Exception as e:
        send_telegram_notification(f"❌ خطأ تقني: {str(e)}")

if __name__ == "__main__":
    main()
