import os
import pandas as pd
import json
import time
from Scraper import SupabaseScraper

CACHE_FILE = "images_cache.json"

def git_push_progress(count):
    """حفظ التقدم ورفعه إلى GitHub"""
    try:
        os.system('git config --local user.email "action@github.com"')
        os.system('git config --local user.name "GitHub Action"')
        os.system(f'git add {CACHE_FILE} Across_MENA_Final_Report.csv')
        os.system(f'git commit -m "تحديث تلقائي: صيد {count} منتج جديد بـ 6 صور"')
        os.system('git push')
        print(f"☁️ [GitHub] تم رفع التحديثات بنجاح!")
    except Exception as e:
        print(f"⚠️ فشل الرفع لـ GitHub: {e}")

def main():
    scraper = SupabaseScraper()
    csv_file = "data.csv"
    
    if not os.path.exists(csv_file):
        print("❌ الملف data.csv غير موجود!")
        return

    # قراءة البيانات الأصلية
    df_input = pd.read_csv(csv_file)
    raw_data = df_input.to_dict(orient='records')

    # تحميل الكاش الحالي أو إنشاء واحد جديد
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                image_cache = json.load(f)
        except:
            image_cache = {}
    else:
        image_cache = {}

    final_list = []
    updated_count = 0

    for index, item in enumerate(raw_data):
        # استخدام معرف فريد لكل مادة
        item_id = str(item.get('id', index))
        
        # القوة هنا: إذا كانت القائمة فارغة [] أو غير موجودة، سيعيد البحث عنها
        # لن يتخطى المادة إلا إذا وجد قائمة تحتوي فعلياً على روابط صور
        existing_images = image_cache.get(item_id, [])
        if isinstance(existing_images, list) and len(existing_images) >= 6:
            item['image_urls'] = existing_images
            final_list.append(item)
            continue

        brand = str(item.get('brand', '')).replace('nan', '')
        model = str(item.get('model', '')).replace('nan', '')
        
        print(f"📡 جاري صيد (6 صور) لـ: {brand} {model} [{index+1}/{len(raw_data)}]")
        
        # استدعاء السكرابر لجلب 6 صور
        new_images = scraper.get_real_images(brand, model)
        
        # تحديث الكاش والقائمة
        image_cache[item_id] = new_images
        item['image_urls'] = new_images
        final_list.append(item)
        updated_count += 1

        # رفع التقدم كل 30 عملية صيد ناجحة لضمان عدم ضياع التعب
        if updated_count > 0 and updated_count % 30 == 0:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(image_cache, f, ensure_ascii=False, indent=4)
            pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
            git_push_progress(updated_count)

    # الحفظ النهائي الشامل
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(image_cache, f, ensure_ascii=False, indent=4)
    pd.DataFrame(final_list).to_csv("Across_MENA_Final_Report.csv", index=False, encoding='utf-8-sig')
    git_push_progress("المهمة كاملة")
    print("🏁 انتهى الصيد بنجاح!")

if __name__ == "__main__":
    main()
