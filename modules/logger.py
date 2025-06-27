# modules/logger.py

import csv
from datetime import datetime
import os

#  Define the full path to the folder
LOG_FILE = r"C:\Users\GHOSEIKW\NESTLE\PA Solutions Innovation and Data Science - Documents\Projects\eQ8-SWP Piloting\access_log.csv"

def log_access(email, page=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page_accessed = page if page else "Login"

    file_exists = os.path.isfile(LOG_FILE)

    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Email", "DateTime", "Page"])
            writer.writerow([email, now, page_accessed])
    except Exception as e:
        print(f"[LOGGING ERROR] Could not write to log file: {e}")
