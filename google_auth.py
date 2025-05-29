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
    "BE": lambda: f"+32 4{random.randint(70,99)} {random.randint(100,999)} {random.randint(100,999)}",
    "FR": lambda: f"+33 6 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    "DE": lambda: f"+49 15{random.randint(0,9)} {random.randint(100,999)} {random.randint(1000,9999)}",
    "CH": lambda: f"+41 7{random.randint(0,9)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}",
    "IT": lambda: f"+39 3{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
    "ES": lambda: f"+34 6{random.randint(0,9)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    "MA": lambda: f"+212 6{random.randint(0,9)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
    "UK": lambda: f"+44 7{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
    "SE": lambda: f"+46 7{random.randint(0,9)} {random.randint(100,999)} {random.randint(100,999)}",
    "PT": lambda: f"+351 9{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
    "NL": lambda: f"+31 6 {random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}"
}

# =============== STEMDATA GENEREREN ===============
random.seed(SEED)
np.random.seed(SEED)
records = []
now = datetime.now()

for country, number_func in country_mobile_formats.items():
    for _ in range(VOTES_PER_COUNTRY):
        song = random.randint(1, 25)
        number = number_func()
        time_offset = timedelta(seconds=random.randint(0, 3600))
        timestamp = (now - time_offset).strftime("%Y-%m-%dT%H:%M:%S")
        records.append([country, number, song, timestamp])

df = pd.DataFrame(records, columns=["COUNTRY CODE", "MOBILE NUMBER", "SONG NUMBER", "TIMESTAMP"])
# Display the first few rows
print(df.head(10))
df.to_csv(OUTPUT_FILE, index=False, sep="\t")
print(df["COUNTRY CODE"].value_counts())

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
