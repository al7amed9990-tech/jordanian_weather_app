import os
import time
import requests
from datetime import datetime, timedelta

def download_latest_refc():
    """تنزيل أحدث ملفات الانعكاسية من GFS لليمن"""
    now = datetime.utcnow() - timedelta(hours=3.5)
    date_str = now.strftime("%Y%m%d")
    hour = now.hour

    if hour >= 18: run_str = "18"
    elif hour >= 12: run_str = "12"
    elif hour >= 6: run_str = "06"
    else: run_str = "00"

    output_dir = os.path.join("static", "maps")
    os.makedirs(output_dir, exist_ok=True)

    print(f"🔄 جاري التحقق من تحديثات دورة: {date_str}_{run_str}Z")

if __name__ == "__main__":
    download_latest_refc()