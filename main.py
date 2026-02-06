import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def main():
    print(f"🚀 بدء التشغيل من الملف المحلي: {datetime.now()}")
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    # 1. قراءة البيانات من الملف اللي رفعته يا عيسى
    if os.path.exists(csv_file):
        try:
            # نحاول قراءة الملف مع التعامل مع ترميزات مختلفة لضمان نجاح القراءة
            try:
                df_input = pd.read_csv(csv_file, encoding='utf-8')
            except:
                df_input = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            raw_data = df_input.to_dict(orient='records')
            print(f"✅ تم تحميل {len(raw_data)} مادة من ملف data.csv")
        except Exception as e:
            print(f"❌ فشل قراءة ملف CSV: {e}")
            return
    else:
        print("❌ ملف data.csv غير موجود في المستودع!")
        return

    # 2. تحميل كاش الصور (عشان يكمل من مطرح ما وقفنا)
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                image_cache = json.load(f)
            print(f"📦 تم تحميل الكاش: {len(image_cache)} مادة موجودة مسبقاً.")
        except:
            image_cache = {}
    else:
        image_cache = {}

    final_list = []
    new_images_count = 0
    total_items = len(raw_data)

    # 3. معالجة الصور
    for index, item in enumerate(raw_data):
        # نستخدم الـ id أو الموديل كمفتاح
        item_id = str(item.get('id', item.get('model', index)))
        
        if item_id in image_cache and len(image_cache[item_id]) > 0:
            item_images = image_cache[item_id]
        else:
            brand = str(item.get('brand', ''))
            model = str(item.get('model', ''))
            print(f"🔍 [{index+1}/{total_items}] سحب صور لـ: {brand} {model}")
            
            item_images = scraper.get_real_images(brand, model)
            image_cache[item_id] = item_images
            new_images_count += 1
            
            # حفظ الكاش كل 20 عملية لضمان عدم ضياع التعب
            if new_images_count % 20 == 0:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(image_cache, f, ensure_ascii=False, indent=4)
                time.sleep(0.5)

        item['image_urls'] = item_images
        final_list.append(item)

    # 4. حفظ الكاش النهائي والملف الجديد
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_cache, f, ensure_ascii=False, indent=4)

    df_final = pd.DataFrame(final_list)
    output_file = "Across_MENA_Final_Report.csv"
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

    # 5. إرسال التقرير لتليجرام
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    if bot_token and chat_id:
        report_text = (
            f"✅ اكتملت المهمة بنجاح (بدون سوبابيس)\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📦 إجمالي المواد: {len(df_final)}\n"
            f"📸 صور جديدة مضافة: {new_images_count}\n"
            f"📂 اسم الملف الجديد: {output_file}"
        )
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': report_text})
            with open(output_file, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", data={'chat_id': chat_id}, files={'document': f})
        except:
            print("⚠️ فشل إرسال التقرير لتليجرام.")

    print(f"🏁 العملية انتهت. تم معالجة {total_items} مادة.")

if __name__ == "__main__":
    main()
