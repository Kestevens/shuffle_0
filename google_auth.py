# GENERATE SOME VOTE DATA AND UPLOAD TO GOOGLE DRIVE VIA SERVICE ACCOUNT

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============================
# 1. GENEREER STEMDATA
# =============================

np.random.seed(42)
num_records = 1000

data = {
    "COUNTRY CODE": ["SE"] * num_records,
    "MOBILE NUMBER": [],
    "SONG NUMBER": np.random.randint(1, 26, num_records),
    "TIMESTAMP": []
}

current_time = datetime.now()
for _ in range(num_records):
    first_part = random.randint(70, 99)
    second_part = random.randint(100, 999)
    third_part = random.randint(100, 999)
    mobile_number = f"+46 {first_part} {second_part} {third_part}"
    data["MOBILE NUMBER"].append(mobile_number)

for i in range(num_records):
    random_seconds = random.randint(0, 3600)
    timestamp = current_time - timedelta(seconds=random_seconds)
    data["TIMESTAMP"].append(timestamp)

df = pd.DataFrame(data)
output_file = "generated_votes_se.txt"
df.to_csv(output_file, sep="\t", index=False)

print(df.head(5))
print(f"\n{output_file} is aangemaakt.")

# =============================
# 2. UPLOAD NAAR GOOGLE DRIVE
# =============================

# Configuratie
SERVICE_ACCOUNT_FILE = "/root/.config/service_account.json"  # JSON bestand van Google
FOLDER_ID = "1EYf9den2D8IVAGvVDrH1ACp6C89z7p1f"  # Map-ID van je gedeelde Drive-map

# Authenticatie met service account
credentials = service_account.Credentials.from_service_account_file(
    "/root/.config/service_account.json"
)

service = build("drive", "v3", credentials=credentials)

# Upload bestand
file_metadata = {
    "name": output_file,
    "parents": [FOLDER_ID]
}
media = MediaFileUpload(output_file, mimetype="text/plain")

uploaded_file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id"
).execute()

print(f"✅ Bestand succesvol geüpload naar Google Drive met ID: {uploaded_file.get('id')}")

