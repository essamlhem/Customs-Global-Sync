import os, requests, pandas as pd, json, time
from Scraper import SupabaseScraper
import local_data

CACHE_FILE = "images_cache.json"

def main():
    scraper = SupabaseScraper()
    
    # 1. محاولة جلب الداتا
    raw_data = scraper.fetch_raw_data()
    
    # 2. الخطة البديلة (Backup)
    if raw_data:
        local_data.save_to_local(raw_data)
        print("✅ تم جلب البيانات وتحديث النسخة المحلية.")
    else:
        raw_data = local_data.load_from_local()
        if not raw_data:
            print("❌ السيرفر محظور ولا توجد نسخة محلية بعد.")
            return
        print("📦 العمل جاري على النسخة المحفوظة محلياً.")

    # 3. تحميل كاش الصور
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f: image_cache = json.load(f)
    else: image_cache = {}

    final_list = []
    new_images = 0
    total = len(raw_data)

    for index, item in enumerate(raw_data):
        item_id = str(item.get('id', index))
        if item_id in image_cache and len(image_cache[item_id]) > 0:
            item['image_urls'] = image_cache[item_id]
        else:
            print(f"🔍 [{index+1}/{total}] سحب صور لـ: {item.get('brand')} {item.get('model')}")
            imgs = scraper.get_real_images(item.get('brand',''), item.get('model',''))
            image_cache[item_id] = imgs
            item['image_urls'] = imgs
            new_images += 1
            if new_images % 20 == 0:
                with open(CACHE_FILE, 'w') as f: json.dump(image_cache, f)

    with open(CACHE_FILE, 'w') as f: json.dump(image_cache, f)

    # 4. تصدير CSV كامل
    df = pd.DataFrame(final_list)
    file_name = "Across_MENA_Full_Report.csv"
    df.to_csv(file_name, index=False, encoding='utf-8-sig')

    # 5. تليجرام
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if bot_token and chat_id:
        msg = f"✅ التقرير جاهز!\n📦 المواد: {len(df)}\n📸 صور جديدة: {new_images}"
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={'chat_id': chat_id, 'text': msg})
        with open(file_name, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendDocument", data={'chat_id': chat_id}, files={'document': f})

if __name__ == "__main__":
    main()
