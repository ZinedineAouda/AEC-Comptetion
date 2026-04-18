import json
import os
import unicodedata

def normalize(name):
    if not name: return ""
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    return n.upper().strip().replace("-", "").replace(" ", "")

def separate_layers():
    DATA_DIR = r"c:\Users\zined\Documents\GitHub\AEC-Comptetion\data"
    ATTITUDE_SOURCE = os.path.join(DATA_DIR, "Algeria Communes attitude.geojson")
    SHAPES_SOURCE = os.path.join(DATA_DIR, "Algeria Communes.geojson")
    
    ATTITUDE_TARGET = os.path.join(DATA_DIR, "Algeria Communes attitude.geojson")
    SHAPES_TARGET = os.path.join(DATA_DIR, "Algeria Communes.geojson")

    # 1. Load the original Attitude attributes (which I had merged but hopefully it's still accessible or I can use the registry)
    # Actually, I'll read the 'Clipped' or 'seismic_registry' if I need a ground truth, 
    # but I'll try to extract them from the current merged file and then clean it up.
    
    print("Loading current merged data...")
    with open(SHAPES_SOURCE, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    # These are the fields we want to move to the 'Attitude' layer
    RISK_FIELDS = [
        "WILAYA", "COMMUNE", "DEGREE\nOF RISK", "ACCEL\nCOEFF A", 
        "CAPITAL ASSUR\ufffd\n(TOTAL)", "GAM RETENTION\n30% (TOTAL)", 
        "PRIME NETTE\n(TOTAL)", "GAM PRIME\n30% (TOTAL)", 
        "MAX DAMAGE\n(TOTAL)", "GAM MAX DAMAGE\n30% (TOTAL)", 
        "AVG RISK\nRATIO", "zone_rpa"
    ]

    attitude_features = []
    purified_commune_features = []

    print("Splitting layers...")
    for f in master_data["features"]:
        props = f["properties"]
        geom = f["geometry"]
        
        # Create Attitude Feature (if it has risk data)
        # We only create a feature in the Attitude layer if it has risk markers
        if "DEGREE\nOF RISK" in props or "zone_rpa" in props:
            # Clone geometry and only keep Risk props
            att_props = {k: props[k] for k in RISK_FIELDS if k in props}
            # Also keep Name for tooltips
            att_props["NAME"] = props.get("NAME_2") or props.get("COMMUNE")
            
            attitude_features.append({
                "type": "Feature",
                "properties": att_props,
                "geometry": geom
            })
        
        # Purify Commune Feature (Remove Risk props)
        purified_props = {k: v for k, v in props.items() if k not in RISK_FIELDS}
        # Keep zone_rpa for the main map if needed, but the user said "dont merge", 
        # so I'll keep ONLY financial props in the Communes layer.
        
        purified_commune_features.append({
            "type": "Feature",
            "properties": purified_props,
            "geometry": geom
        })

    # Save Attitude Layer
    att_collection = {
        "type": "FeatureCollection",
        "name": "Algeria Communes attitude",
        "features": attitude_features
    }
    with open(ATTITUDE_TARGET, "w", encoding="utf-8") as f:
        json.dump(att_collection, f, indent=2)
    print(f"Saved independent Attitude layer with {len(attitude_features)} spatial features.")

    # Save Purified Communes Layer
    comm_collection = {
        "type": "FeatureCollection",
        "name": "Algeria Communes",
        "features": purified_commune_features
    }
    with open(SHAPES_TARGET, "w", encoding="utf-8") as f:
        json.dump(comm_collection, f, indent=2)
    print(f"Saved purified Communes layer with {len(purified_commune_features)} features.")

if __name__ == "__main__":
    separate_layers()
