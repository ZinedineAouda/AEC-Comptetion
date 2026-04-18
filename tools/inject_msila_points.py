import json
import os

def inject_msila_points():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    GEOJSON_PATH = os.path.join(DATA_DIR, "Clipped.geojson")
    
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Missing Communes from RPA 2003 Annex for M'Sila (Group A)
    # Coordinates sourced from official geographical registries
    missing_communes = [
        {"name": "Belaiba", "coords": [5.1954, 35.5744]},
        {"name": "Beni Ilmane", "coords": [4.0900, 35.9546]},
        {"name": "Maadid", "coords": [4.7485, 35.7999]},
        {"name": "Mtarfa", "coords": [4.6244, 35.7176]},
        {"name": "Ouled Addi Guebala", "coords": [4.8728, 35.7078]},
        {"name": "Ouled Mansour", "coords": [4.3771, 35.7268]},
        {"name": "Tarmount", "coords": [4.2830, 35.8170]},
        {"name": "Hammam Dhalaa", "coords": [4.4167, 35.8500]} # Injecting a local M'Sila point
    ]
    
    print(f"Injecting {len(missing_communes)} missing M'Sila communes...")
    
    for c in missing_communes:
        # Check if already exists (fuzzy)
        exists = any(f["properties"] and f["properties"].get("NAME") and c["name"].upper() in f["properties"].get("NAME", "").upper() for f in data["features"])
        if not exists:
            new_feature = {
                "type": "Feature",
                "properties": {
                    "NAME": c["name"],
                    "SOURCE": "RPA_SURGICAL_INJECTION"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": c["coords"]
                }
            }
            data["features"].append(new_feature)
            print(f"  + Added: {c['name']}")
        else:
            print(f"  - Skipped (Already exists): {c['name']}")

    with open(GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print("Injection complete.")

if __name__ == "__main__":
    inject_msila_points()
