import os, time, requests, dotenv, pandas as pd

dotenv.load_dotenv()
BASE_URL  = os.getenv("SUPABASE_URL")           # e.g. https://db.gttiunvrapfjxilkkjsj.supabase.co
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
assert BASE_URL and SERVICE_KEY, "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY"

API   = "https://api.fda.gov/device/enforcement.json"
LIMIT = 100
HEAD  = {"User-Agent": "Mozilla/5.0"}

def fetch(year: int, skip: int) -> list[dict]:
    url = f"{API}?search=report_date:[{year}0101+TO+{year}1231]&limit={LIMIT}&skip={skip}"
    r   = requests.get(url, headers=HEAD, timeout=30)
    if r.status_code == 404:
        return []
    if r.status_code == 429:            # throttled: wait & retry
        time.sleep(2)
        return fetch(year, skip)
    r.raise_for_status()
    return r.json()["results"]

def upsert_batch(rows: list[dict]):
    url = f"{BASE_URL}/rest/v1/recalls_raw"
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Prefer": "resolution=ignore-duplicates",
        "Content-Type": "application/json"
    }
    requests.post(url, json=rows, headers=headers, timeout=30).raise_for_status()

inserted = 0
for year in range(2002, 2025):
    skip = 0
    while True:
        rows = fetch(year, skip)
        if not rows:
            break

        df = pd.DataFrame(rows)
        df.columns = [c.lower() for c in df.columns]

        batch = df[
            ["recall_number",
             "event_id",
             "recall_initiation_date",
             "classification",
             "product_description"]
        ].to_dict("records")

        upsert_batch(batch)
        inserted += len(batch)
        skip += LIMIT

        if inserted % 5000 == 0:
            print(f"...{inserted} rows processed so far (through {year})")

        time.sleep(0.25)   # stay well under rate limit

print(f"✓ Finished. Processed {inserted} rows total.")
