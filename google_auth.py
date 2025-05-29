# MULTICOUNTRY VOTE GENERATOR + GOOGLE DRIVE UPLOAD
import os
import json
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import subprocess

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============== INSTELLINGEN ===============
SEED = 42
VOTES_PER_COUNTRY = 100
OUTPUT_FILE = "generated_votes.txt"
DRIVE_FOLDER_ID = "1EYf9den2D8IVAGvVDrH1ACp6C89z7p1f"  # jouw map-ID op Drive
SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"
GITHUB_REPO = "https://github.com/Kestevens/shuffle_0.git"

# =============== CLONE VAN GITHUB ===============
if not os.path.exists("shuffle_0"):
    subprocess.run(["git", "clone", GITHUB_REPO])

# =============== LANDEN & FORMATEN ===============
country_mobile_formats = {
    "BE": "+32 4{0:02d} {1:03d} {2:03d}",
    "FR": "+33 6 {0:02d} {1:02d} {2:02d} {3:02d}",
    "DE": "+49 15{0:01d} {1:03d} {2:04d}",
    "CH": "+41 7{0:01d} {1:03d} {2:02d} {3:02d}",
    "IT": "+39 3{0:02d} {1:03d} {2:03d}",
    "ES": "+34 6{0:01d} {1:02d} {2:02d} {3:02d}",
    "MA": "+212 6{0:01d} {1:02d} {2:02d} {3:02d}",
    "UK": "+44 7{0:02d} {1:03d} {2:04d}",
    "SE": "+46 7{0:01d} {1:03d} {2:03d}",
    "PT": "+351 9{0:02d} {1:03d} {2:03d}",
    "NL": "+31 6 {0:02d} {1:03d} {2:03d}"
}

def generate_mobile_number(country):
    fmt = country_mobile_formats[country]
    args = tuple(random.randint(0, 99) for _ in fmt.count('{'))
    return fmt.format(*args)

# =============== STEMDATA GENEREREN ===============
random.seed(SEED)
np.random.seed(SEED)
records = []
now = datetime.now()

for country in country_mobile_formats:
    for _ in range(VOTES_PER_COUNTRY):
        song = random.randint(1, 25)
        number = generate_mobile_number(country)
        time_offset = timedelta(seconds=random.randint(0, 3600))
        timestamp = (now - time_offset).strftime("%Y-%m-%dT%H:%M:%S")
        records.append([country, number, song, timestamp])

df = pd.DataFrame(records, columns=["COUNTRY CODE", "MOBILE NUMBER", "SONG NUMBER", "TIMESTAMP"])
df.to_csv(OUTPUT_FILE, index=False, sep="\t")

print(f"📄 {OUTPUT_FILE} aangemaakt met {len(df)} stemmen uit {len(country_mobile_formats)} landen.")

# =============== AUTHENTICATIE GOOGLE DRIVE ===============
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
service = build("drive", "v3", credentials=creds)

# =============== UPLOAD NAAR DRIVE ===============
file_metadata = {
    "name": OUTPUT_FILE,
    "parents": [DRIVE_FOLDER_ID]
}
media = MediaFileUpload(OUTPUT_FILE, mimetype="text/plain")
uploaded_file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id"
).execute()

print(f"✅ Bestand succesvol geüpload naar Google Drive (ID: {uploaded_file.get('id')})")
