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

def get_commune_name(props):
    # Try common nomenclature patterns
    for key in ["NAME", "NAME_2", "COMMUNE", "Commune", "NOM_COMM"]:
        if key in props and props[key]:
            return props[key]
    return ""

def sync_file(file_path, registry, wilaya_boundaries, wilaya_overrides):
    print(f"Syncing: {os.path.basename(file_path)}...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    counts = {"match": 0, "spatial": 0, "fallback": 0}
    
    for feature in geo_data["features"]:
        props = feature["properties"]
        geom = feature["geometry"]
        if not geom: continue
        
        # Determine coordinates (Handle Points and Polygons)
        if geom["type"] == "Point":
            px, py = geom["coordinates"]
        else:
            # For Polygons, use a simple centroid/first-point representative for spatial join
            try:
                if geom["type"] == "Polygon":
                    px, py = geom["coordinates"][0][0]
                elif geom["type"] == "MultiPolygon":
                    px, py = geom["coordinates"][0][0][0]
                else: continue
            except: continue

        raw_comm_name = get_commune_name(props)
        n_name = normalize_match(raw_comm_name)

        found_zone = None
        
        # 1. First, find Physical Wilaya
        parent_w = None
        for w in wilaya_boundaries:
            if is_point_in_multipoly(px, py, w["coords"]):
                parent_w = w; break
        
        if parent_w:
            w_name = parent_w["name"]
            local_overrides = wilaya_overrides.get(w_name, {})
            if n_name in local_overrides:
                found_zone = local_overrides[n_name]
                counts["match"] += 1
            else:
                matches = difflib.get_close_matches(n_name, list(local_overrides.keys()), n=1, cutoff=0.6)
                if matches:
                    found_zone = local_overrides[matches[0]]
                    counts["match"] += 1
                else:
                    found_zone = parent_w["info"]["default"]
                    counts["spatial"] += 1
        else:
            found_zone = "I"
            counts["fallback"] += 1

        props["zone_rpa"] = found_zone
        # Clean up legacy names if present
        if "DEGREE\nOF RISK" in props: props["zone_rpa_legacy"] = props.pop("DEGREE\nOF RISK")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(geo_data, f, indent=2)
    
    print(f"  Done. Matches: {counts['match']} | Spatial: {counts['spatial']} | Fallback: {counts['fallback']}")

def bulk_sync():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    GEOJSON_WILAYAS = os.path.join(DATA_DIR, "gadm41.geojson")
    REGISTRY_PATH = os.path.join(DATA_DIR, "seismic_registry_rpa.json")

    print(f"Loading Global Registry...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    wilaya_overrides = {}
    for w_name, w_info in registry.items():
        norm_w = normalize_match(w_name)
        wilaya_overrides[norm_w] = {}
        for zone, communes in w_info.get("groups", {}).items():
            for c in communes:
                nc = normalize_match(c)
                wilaya_overrides[norm_w][nc] = zone
                if norm_w == "M'SILA":
                    if "ILMANE" in nc: wilaya_overrides[norm_w]["ILMENE"] = zone
                    if "GUEBALA" in nc: wilaya_overrides[norm_w]["ADDI"] = zone
                    if "DHALAA" in nc: wilaya_overrides[norm_w]["DELAA"] = zone
                    if "KHADRA" in nc: wilaya_overrides[norm_w]["KADRA"] = zone

    print(f"Loading Wilaya Reference Boundaries...")
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

    # Files to process
    targets = [
        "Clipped.geojson", 
        "Algeria Communes.geojson", 
        "Algeria Communes attitude.geojson"
    ]
    
    for t in targets:
        p = os.path.join(DATA_DIR, t)
        if os.path.exists(p):
            sync_file(p, registry, wilaya_boundaries, wilaya_overrides)

if __name__ == "__main__":
    bulk_sync()
