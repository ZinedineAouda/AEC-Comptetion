import json
import os
import unicodedata

def normalize(name):
    if not name: return ""
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    return n.upper().strip().replace("-", "").replace(" ", "")

def merge_attitude_data():
    DATA_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion\data"
    ATTITUDE_PATH = os.path.join(DATA_DIR, "Algeria Communes attitude.geojson")
    SHAPES_PATH = os.path.join(DATA_DIR, "Algeria Communes.geojson")
    OUTPUT_PATH = os.path.join(DATA_DIR, "Algeria Communes.geojson") # Overwrite

    print("Loading Attitude attributes...")
    with open(ATTITUDE_PATH, "r", encoding="utf-8") as f:
        attr_data = json.load(f)
    
    db = {}
    for f in attr_data["features"]:
        p = f["properties"]
        w = normalize(p.get("WILAYA", ""))
        c = normalize(p.get("COMMUNE", ""))
        key = f"{w}|{c}"
        db[key] = p

    print("Loading Spatial shapes...")
    with open(SHAPES_PATH, "r", encoding="utf-8") as f:
        shapes_data = json.load(f)

    print("Merging data...")
    merged_count = 0
    for f in shapes_data["features"]:
        p = f["properties"]
        # GADM names are NAME_1 (Wilaya) and NAME_2 (Commune)
        w = normalize(p.get("NAME_1", ""))
        c = normalize(p.get("NAME_2", ""))
        key = f"{w}|{c}"
        
        if key in db:
            # Merge and parse numbers
            for k, v in db[key].items():
                # Clean numeric strings like "1,234.56"
                if isinstance(v, str) and (',' in v or (v.replace('.', '', 1).isdigit() and '.' in v)):
                    try:
                        clean_v = v.replace(',', '')
                        p[k] = float(clean_v)
                    except:
                        p[k] = v
                else:
                    p[k] = v
            
            merged_count += 1
            # Standardize the zone_rpa if it's there
            if "DEGREE\nOF RISK" in p:
                p["zone_rpa"] = str(p["DEGREE\nOF RISK"])

    print(f"Successfully merged {merged_count} communes.")
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(shapes_data, f, indent=2)
    print("Saved merged layer to Algeria Communes.geojson")

if __name__ == "__main__":
    merge_attitude_data()
