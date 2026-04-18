import json
import os

def round_coords(coords, precision=4):
    """Recursively round coordinates to a specific precision."""
    if isinstance(coords, (int, float)):
        return round(float(coords), precision)
    return [round_coords(c, precision) for c in coords]

def optimize_geojson():
    BASE_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion"
    DATA_PATH = os.path.join(BASE_DIR, "data", "gam_prime_net.geojson")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: File not found at {DATA_PATH}")
        return

    orig_size = os.path.getsize(DATA_PATH)
    print(f"Optimizing {DATA_PATH} (Source Size: {orig_size / 1024 / 1024:.2f} MB)...")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Required properties for the dashboard logic
    KEEP_PROPS = {"NAME_1", "NAME_2", "NAME", "commune", "gam_prime", "zone_rpa"}
    
    processed_count = 0
    for feature in data.get("features", []):
        # 1. Round Coordinates
        if "geometry" in feature and "coordinates" in feature["geometry"]:
            feature["geometry"]["coordinates"] = round_coords(feature["geometry"]["coordinates"], 4)
        
        # 2. Prune Properties
        props = feature.get("properties", {})
        new_props = {k: v for k, v in props.items() if k in KEEP_PROPS}
        feature["properties"] = new_props
        
        processed_count += 1

    # Save as minified JSON (separators=(',', ':'))
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(',', ':'))

    new_size = os.path.getsize(DATA_PATH)
    reduction = (1 - (new_size / orig_size)) * 100
    
    print(f"Optimization complete!")
    print(f"Features Processed: {processed_count}")
    print(f"New Size: {new_size / 1024 / 1024:.2f} MB")
    print(f"Size Reduction: {reduction:.1f}%")

if __name__ == "__main__":
    optimize_geojson()
