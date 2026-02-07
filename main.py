import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def main():
    print(f"🚀 بدء التشغيل: {datetime.now()}")
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    # 1. قراءة البيانات المحلية
    if not os.path.exists(csv_file):
        print("❌ ملف data.csv غير موجود!")
        return
    
    try:
        df_input = pd.read_csv(csv_file)
        raw_data = df_input.to_dict(orient='records')
        print(f"✅ تم تحميل {len(raw_data)} مادة.")
    except Exception as e:
        print(f"❌ خطأ في قراءة CSV: {e}")
        return

    # 2. تحميل الكاش (المواد المنجزة سابقاً)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            image_cache = json.load(f)
        print(f"📦 تم العثور على كاش يحتوي على {len(image_cache)} مادة.")
    else:
        image_cache = {}

    final_list = []
    new_images_count = 0
    total_items = len(raw_data)

    # 3. معالجة البيانات مع خاصية الاستكمال (Resume)
    for index, item in enumerate(raw_data):
        # معرف فريد لكل مادة
        item_id = str(item.get('id', f"{item.get('brand')}_{item.get('model')}"))
        
        # إذا كانت المادة موجودة في الكاش وبها صور، نتخطاها
        if item_id in image_cache and image_cache[item_id]:
            item['image_urls'] = image_cache[item_id]
            final_list.append(item)
            continue
        
        # إذا لم تكن موجودة، نبحث عن صورها
        brand = str(item.get('brand', ''))
        model = str(item.get('model', ''))
        print(f"🔍 [{index+1}/{total_items}] سحب صور لـ: {brand} {model}")
        
        imgs = scraper.get_real_images(brand, model)
        image_cache[item_id] = imgs
        item['image_urls'] = imgs
        new_images_count += 1
        final_list.append(item)

        # حفظ الكاش كل 50 صورة لضمان عدم ضياع الجهد إذا فصل السيرفر
        if new_images_count % 50 == 0:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(image_cache, f, ensure_ascii=False, indent=4)
            print(f"💾 تم حفظ تقدم مؤقت ({new_images_count} صورة جديدة)")
            time.sleep(1) # تأخير بسيط لتجنب الحظر

    # 4. حفظ النتائج النهائية
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_cache, f, ensure_ascii=False, indent=4)

    df_final = pd.DataFrame(final_list)
    output_file = "Across_MENA_Final_Report.csv"
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

    # 5. إرسال إشعار تليجرام
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if bot_token and chat_id:
        done_count = len(image_cache)
        msg = (f"⏳ تحديث العمل الدوري:\n"
               f"✅ تم إنجاز: {done_count} من أصل {total_items}\n"
               f"📸 صور جديدة في هذه الدورة: {new_images_count}")
        try:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': msg})
        except: pass

    print(f"🏁 انتهت الدورة الحالية. المنجز الكلي: {len(image_cache)}")

if __name__ == "__main__":
    main()
