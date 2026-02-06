import os
import requests
import pandas as pd
import json
import time
from datetime import datetime
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def main():
    print(f"🚀 بدء التشغيل الذكي: {datetime.now()}")
    scraper = SupabaseScraper()
    image_cache = load_cache()
    
    all_data = []
    offset = 0
    limit = 500 # نسحب 500 مادة في كل طلب لسوبابيس
    
    # 1. جلب كل البيانات من سوبابيس على دفعات
    print("📥 جلب البيانات من Supabase...")
    while True:
        batch = scraper.fetch_raw_data_batched(offset=offset, limit=limit)
        if not batch: break
        all_data.extend(batch)
        offset += limit
        if len(batch) < limit: break # إذا رجع أقل من 500 يعني وصلنا للنهاية
        time.sleep(0.5) # راحة للسيرفر

    print(f"✅ تم جلب {len(all_data)} مادة. نبدأ معالجة الصور...")

    final_list = []
    new_images = 0

    # 2. معالجة الصور (مع استخدام الكاش)
    for item in all_data:
        item_id = str(item.get('id', item.get('hs_code', '')))
        
        if item_id in image_cache and len(image_cache[item_id]) > 0:
            imgs = image_cache[item_id]
        else:
            # نسحب الصور فقط إذا مو موجودة بالكاش
            imgs = scraper.get_real_images(item.get('brand', ''), item.get('model', ''))
            image_cache[item_id] = imgs
            new_images += 1
            if new_images % 10 == 0:
                save_cache(image_cache) # حفظ دوري عشان لو فصل ما نضيع شي
                time.sleep(1)

        item['image_urls'] = imgs # التسمية الجديدة اللي طلبها المبرمج
        final_list.append(item)

    # 3. تنظيف وحفظ الملف
    df = pd.DataFrame(final_list)
    to_drop = ['material', 'note', 'band-material', 'band_material']
    df_final = df.drop(columns=[c for c in to_drop if c in df.columns])
    
    file_name = "Across_MENA_Report.csv"
    df_final.to_csv(file_name, index=False, encoding='utf-8-sig')

    # 4. إرسال لتليجرام
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    msg = f"✅ اكتمل التحديث!\n🔹 المواد: {len(df_final)}\n🔹 صور جديدة: {new_images}"
    
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': msg})
    with open(file_name, 'rb') as f:
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", data={'chat_id': chat_id}, files={'document': f})

if __name__ == "__main__":
    main()
