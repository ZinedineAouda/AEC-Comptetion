import json
import os

def merge_rpa_layers():
    DATA_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion\data"
    UNUSED_DIR = os.path.join(DATA_DIR, "unused")
    os.makedirs(UNUSED_DIR, exist_ok=True)
    
    CLIPPED_PATH = os.path.join(DATA_DIR, "Clipped.geojson")
    GADM_PATH = os.path.join(DATA_DIR, "gadm41.geojson")
    TARGET_PATH = os.path.join(DATA_DIR, "rpa_zone.geojson")

    print("Loading layers...")
    with open(CLIPPED_PATH, "r", encoding="utf-8") as f:
        clipped = json.load(f)
    with open(GADM_PATH, "r", encoding="utf-8") as f:
        gadm = json.load(f)

    # Combine features
    combined_features = gadm["features"] + clipped["features"]

    # Create new collection
    rpa_zone = {
        "type": "FeatureCollection",
        "name": "rpa zone",
        "features": combined_features
    }

    print(f"Merging {len(gadm['features'])} polygons and {len(clipped['features'])} points...")
    with open(TARGET_PATH, "w", encoding="utf-8") as f:
        json.dump(rpa_zone, f, indent=2)
    
    # Archive old files
    for f in ["Clipped.geojson", "gadm41.geojson"]:
        src = os.path.join(DATA_DIR, f)
        dst = os.path.join(UNUSED_DIR, f)
        if os.path.exists(src):
            os.replace(src, dst)
            print(f"Archived {f} to unused/")

    print("Successfully created 'rpa_zone.geojson'")

if __name__ == "__main__":
    merge_rpa_layers()
