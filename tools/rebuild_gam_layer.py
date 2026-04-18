import json
import os
import gzip
import unicodedata
from collections import Counter

# Mirror of main.py normalization for consistent matching
def normalize_match(name: str):
    if not name: return ""
    try:
        # Handle decimal numbers to avoid confusion (e.g. codes)
        text = str(name)
        # Remove "Code - " prefix if present (e.g., "134 - HYDRA")
        if " - " in text:
            text = text.split(" - ")[-1].strip()
            
        n = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    except:
        n = str(name)
    n = n.upper().strip()
    
    n = n.replace("B.B ", "BORDJ BOU ")
    n = n.replace("B.B.", "BORDJ BOU")
    n = n.replace("O.E.B", "OUM EL BOUAGHI")
    n = n.replace("S.B.A", "SIDI BEL ABBES")
    n = n.replace("T.O", "TIZI OUZOU")
    n = n.replace("A.T", "AIN TEMOUCHENT")
    n = n.replace("A.D", "AIN DEFLA")
    n = n.replace("-", " ")
    n = n.replace(".", " ")
    while "  " in n: n = n.replace("  ", " ")
    return n.strip()

def rebuild_gam_layer():
    BASE_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion"
    CACHE_PATH = os.path.join(BASE_DIR, "data", "portfolio_cache.json.gz")
    GEOJSON_PATH = os.path.join(BASE_DIR, "data", "gam_prime_net.geojson")
    
    if not os.path.exists(CACHE_PATH):
        print(f"Error: Cache not found at {CACHE_PATH}")
        return

    print("Loading portfolio data from cache...")
    with gzip.open(CACHE_PATH, 'rb') as f:
        portfolio_data = json.load(f)
    
    profiles = portfolio_data.get("profiles", [])
    print(f"Loaded {len(profiles)} profiles.")

    # Aggregate by commune
    print("Aggregating premiums by commune...")
    commune_totals = Counter()
    for p in profiles:
        c_name = normalize_match(p.get("commune", ""))
        commune_totals[c_name] += p.get("premium", 0.0)

    print(f"Aggregated totals for {len(commune_totals)} unique communes.")

    if not os.path.exists(GEOJSON_PATH):
        print(f"Error: GeoJSON not found at {GEOJSON_PATH}")
        return

    print(f"Updating GeoJSON: {GEOJSON_PATH}...")
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    match_count = 0
    total_injected = 0
    miss_count = 0
    
    for feature in geojson.get("features", []):
        props = feature["properties"]
        # Candidates for commune name in different GeoJSON formats
        candidates = [props.get("NAME_2"), props.get("NAME"), props.get("commune"), props.get("NAME_3")]
        
        found_total = 0.0
        matched_this = False
        for raw_name in candidates:
            if raw_name:
                norm_name = normalize_match(raw_name)
                if norm_name in commune_totals:
                    found_total = commune_totals[norm_name]
                    match_count += 1
                    matched_this = True
                    break
        
        if not matched_this:
            miss_count += 1
            
        props["gam_prime"] = found_total
        total_injected += found_total

    print(f"Matched {match_count} features. Missed {miss_count} features (set to 0.0).")
    print(f"Total premium injected into GeoJSON: {total_injected:,.2f}")

    with open(GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

    print("Rebuild complete. Files are now ready for visualization.")

if __name__ == "__main__":
    rebuild_gam_layer()
