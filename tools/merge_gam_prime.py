import json
import os

def merge_gam_prime():
    SOURCE_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion\data\unused\GAM Prime Net"
    TARGET_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion\data"
    
    files = ["Algeria_communes.geojson", "gadm41.geojson"]
    combined_features = []
    
    print("Combining GAM Prime Net datasets...")
    for f in files:
        path = os.path.join(SOURCE_DIR, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as src:
                data = json.load(src)
                combined_features.extend(data["features"])
                print(f"Added {len(data['features'])} features from {f}")

    output_data = {
        "type": "FeatureCollection",
        "name": "GAM Prime Net",
        "features": combined_features
    }

    output_path = os.path.join(TARGET_DIR, "gam_prime_net.geojson")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    merge_gam_prime()
