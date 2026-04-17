import requests, json

# Test stats
s = requests.get("http://localhost:8000/api/portfolio/stats").json()
print("=== STATS ===")
print(json.dumps(s, indent=2))

# Test paginated data
d = requests.get("http://localhost:8000/api/portfolio/data?offset=0&limit=3").json()
print("\n=== FIRST 3 POLICIES ===")
total = d.get("total", 0)
print(f"Total: {total}")
for p in d["data"]:
    pid = p["policy_id"]
    wil = p["wilaya"]
    zone = p["zone_rpa"]
    cap = p["capital"]
    prem = p["premium"]
    fair = p["fair_premium"]
    label = p["assessment"]["label"]
    revs = p["revision_count"]
    print(f"  {pid} | {wil} | Zone {zone} | Capital {cap:,.0f} | Premium {prem:,.0f} | Fair {fair:,.0f} | {label} | Revs: {revs}")

# Test search
r = requests.get("http://localhost:8000/api/portfolio/search?q=16330").json()
count = r.get("count", 0)
print(f"\n=== SEARCH '16330' === ({count} results)")
for p in r["results"][:3]:
    print(f"  {p['policy_id']} | Revisions: {p['revision_count']}")

# Test sort + filter
d2 = requests.get("http://localhost:8000/api/portfolio/data?offset=0&limit=3&sort_by=capital&sort_dir=desc&filter_zone=III").json()
print(f"\n=== TOP 3 BY CAPITAL (Zone III) === ({d2.get('total',0)} total)")
for p in d2["data"]:
    print(f"  {p['policy_id']} | Capital {p['capital']:,.0f} | {p['assessment']['label']}")
