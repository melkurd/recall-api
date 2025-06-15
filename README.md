# Recall API ⚠️

Instant FDA **medical-device recall** feed (2002 → present) — auto-refreshed every Friday.

## Quick example

```bash
curl -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd0dGl1bnZyYXBmanhpbGtranNqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4NzgxMzksImV4cCI6MjA2NTQ1NDEzOX0._QuuyW_Z_b8yn2GjBiGZ_yvwBdVftjtl6IWHhrfLCbw" \
"https://gttiunvrapfjxilkkjsj.supabase.co/rest/v1/recalls_raw?select=recall_number,recall_initiation_date&limit=5"
```

## Common filters

| purpose            | query piece                                                    |
|--------------------|----------------------------------------------------------------|
| latest 50 recalls  | `order=recall_initiation_date.desc&limit=50`                   |
| only **Class I**   | `recall_classification=eq.Class%20I`                           |
| keyword “catheter” | `product_description=ilike.*catheter*`                         |

## Draft pricing

| plan       | quota       | price  |
|------------|-------------|--------|
| Sandbox    | 100 req/day | free   |
| Starter    | 10 k req/mo | \$99 /mo |
| Pro        | 100 k req/mo| \$299 /mo|
| Enterprise | unlimited + SLA | email |
