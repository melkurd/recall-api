import os, time, requests, psycopg2, dotenv, pandas as pd

dotenv.load_dotenv()
conn_str = os.getenv("SUPABASE_CONN")
if not conn_str:
    raise RuntimeError("SUPABASE_CONN missing in .env")

API   = "https://api.fda.gov/device/enforcement.json"
LIMIT = 100                 # openFDA per-page max
HEAD  = {"User-Agent": "Mozilla/5.0"}

def fetch(year: int, skip: int) -> list[dict]:
    query = f"search=report_date:[{year}0101+TO+{year}1231]"
    url   = f"{API}?{query}&limit={LIMIT}&skip={skip}"
    r     = requests.get(url, headers=HEAD, timeout=30)
    if r.status_code == 404:        # no more pages for this year
        return []
    if r.status_code == 429:        # API throttle; wait & retry
        time.sleep(2)
        return fetch(year, skip)
    r.raise_for_status()
    return r.json()["results"]

with psycopg2.connect(conn_str) as conn, conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recalls_raw (
            recall_number           TEXT PRIMARY KEY,
            event_id                TEXT,
            recall_initiation_date  DATE,
            recall_classification   TEXT,
            product_description     TEXT
        );
    """)
    conn.commit()

    inserted = skipped = 0

    for year in range(2002, 2025):      # inclusive range
        skip = 0
        while True:
            rows = fetch(year, skip)
            if not rows:
                break
            df = pd.DataFrame(rows)
            df.columns = [c.lower() for c in df.columns]

            for _, r in df.iterrows():
                rec = r.get("recall_number")
                if pd.isna(rec):
                    skipped += 1
                    continue
                cur.execute(
                    """INSERT INTO recalls_raw
                       VALUES (%s,%s,%s,%s,%s)
                       ON CONFLICT DO NOTHING""",
                    (
                        str(rec),
                        r.get("event_id"),
                        r.get("recall_initiation_date"),
                        r.get("classification"),
                        str(r.get("product_description"))[:400],
                    ),
                )
                if cur.rowcount:
                    inserted += 1

            conn.commit()
            skip += LIMIT
            if inserted and inserted % 5000 == 0:
                print(f"...{inserted} rows inserted so far (through {year})")
            time.sleep(0.25)            # stay far below 240 req/min

print(f"✓ Finished. Inserted {inserted} rows, skipped {skipped}.")
