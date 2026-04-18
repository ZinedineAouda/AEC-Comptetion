import json
import os
import unicodedata
import shutil
import sys
import difflib

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_match(name: str):
    if not name: return ""
    # Standardize normalization and handle GADM artifacts
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    n = n.upper().strip().replace("-", " ").replace(".", " ").replace("_", " ").replace("'", " ")
    while "  " in n: n = n.replace("  ", " ")
    
    # Surgical aliases for Wilayas
    wilaya_aliases = {
        "TAMANGHASSET": "TAMANRASSET",
        "BJAA": "BEJAIA",
        "AN DEFLA": "AIN DEFLA",
        "SITIF": "SETIF",
        "M SILA": "M'SILA"
    }
    for old, new in wilaya_aliases.items():
        if n == old: n = new
        
    return n.strip()

def is_point_in_poly(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def is_point_in_multipoly(x, y, multipoly):
    for poly_entry in multipoly:
        for ring in poly_entry:
            if is_point_in_poly(x, y, ring): return True
    return False

def sync_rpa_scoped_fuzzy():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    GEOJSON_POINTS = os.path.join(DATA_DIR, "Clipped.geojson")
    GEOJSON_WILAYAS = os.path.join(DATA_DIR, "gadm41.geojson")
    REGISTRY_PATH = os.path.join(DATA_DIR, "seismic_registry_rpa.json")
    BACKUP_PATH = os.path.join(DATA_DIR, "Clipped.geojson.bak")

    print(f"Loading Global Registry...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    # Pre-calculate normalized override indices per Wilaya
    wilaya_overrides = {}
    for w_name, w_info in registry.items():
        norm_w = normalize_match(w_name)
        wilaya_overrides[norm_w] = {}
        for zone, communes in w_info.get("groups", {}).items():
            for c in communes:
                nc = normalize_match(c)
                wilaya_overrides[norm_w][nc] = zone
                # Add surgical aliases for M'Sila
                if norm_w == "M'SILA":
                    if "ILMANE" in nc: wilaya_overrides[norm_w]["ILMENE"] = zone
                    if "GUEBALA" in nc: wilaya_overrides[norm_w]["ADDI"] = zone
                    if "DHALAA" in nc: wilaya_overrides[norm_w]["DELAA"] = zone
                    if "KHADRA" in nc: wilaya_overrides[norm_w]["KADRA"] = zone

    print(f"Loading Wilaya Boundaries...")
    with open(GEOJSON_WILAYAS, "r", encoding="utf-8") as f:
        wilaya_geo = json.load(f)

    wilaya_boundaries = []
    norm_registry = {normalize_match(k): v for k, v in registry.items()}
    
    for feature in wilaya_geo["features"]:
        raw_name = feature["properties"].get("NAME_1", "")
        norm_name = normalize_match(raw_name)
        geometry = feature["geometry"]
        wilaya_boundaries.append({
            "name": norm_name,
            "coords": geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]],
            "info": norm_registry.get(norm_name, {"default": "I"})
        })

    print(f"Processing Points with Scoped Fuzzy Logic...")
    with open(GEOJSON_POINTS, "r", encoding="utf-8") as f:
        points_geo = json.load(f)

    if not os.path.exists(BACKUP_PATH): shutil.copy2(GEOJSON_POINTS, BACKUP_PATH)

    counts = {"match": 0, "spatial": 0, "fallback": 0}
    
    for feature in points_geo["features"]:
        props = feature["properties"]
        geom = feature["geometry"]
        if not geom or "coordinates" not in geom: continue
        px, py = geom["coordinates"]
        n_name = normalize_match(props.get("NAME", ""))

        found_zone = None
        
        # 1. First, find Physical Wilaya
        parent_w = None
        for w in wilaya_boundaries:
            if is_point_in_multipoly(px, py, w["coords"]):
                parent_w = w; break
        
        if parent_w:
            w_name = parent_w["name"]
            # 2. Localized Fuzzy Override Search (Scoped to this wilaya)
            local_overrides = wilaya_overrides.get(w_name, {})
            if n_name in local_overrides:
                found_zone = local_overrides[n_name]
                counts["match"] += 1
            else:
                # Fuzzy match within this wilaya list
                matches = difflib.get_close_matches(n_name, list(local_overrides.keys()), n=1, cutoff=0.6)
                if matches:
                    found_zone = local_overrides[matches[0]]
                    counts["match"] += 1
                else:
                    # Final fallback: parent defaults
                    found_zone = parent_w["info"]["default"]
                    counts["spatial"] += 1
        else:
            # Totally outside all polygons (shouldn't happen with GADM usually)
            found_zone = "I"
            counts["fallback"] += 1

        props["zone_rpa"] = found_zone

    print(f"Scoped Sync Complete!")
    print(f"  - Localized Matches: {counts['match']}")
    print(f"  - Wilaya Defaults: {counts['spatial']}")
    
    # Audit Checklist
    msila_targets = ["M'Sila", "Dhalaa", "Beni Ilmene", "Magra", "Berhoum", "Ouled Derradj", "Addi", "Ouanougha", "Khadra"]
    found_msila = []
    for f in points_geo["features"]:
        nm = str(f['properties'].get('NAME', ''))
        zr = f['properties'].get('zone_rpa', '')
        if any(t in nm for t in msila_targets) and zr == 'IIa':
            found_msila.append(nm)
    
    print(f"Verified IIa Points in M'Sila Area: {len(set(found_msila))}")
    print(f"Examples: {list(set(found_msila))[:5]}")

    with open(GEOJSON_POINTS, "w", encoding="utf-8") as f:
        json.dump(points_geo, f, indent=2)

if __name__ == "__main__":
    sync_rpa_scoped_fuzzy()
