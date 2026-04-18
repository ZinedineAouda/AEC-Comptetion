from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import sys
import unicodedata

# Ensure backend can find its modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monte_carlo_simulator import monte_carlo_engine
from catboost_engine import engine as catboost_engine

app = FastAPI(title="AEC RPA-Integrated Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load RPA Registry
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
REGISTRY_PATH = os.path.join(DATA_DIR, "seismic_registry_rpa.json")

try:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        rpa_data = json.load(f)
except Exception as e:
    print(f"Warning: RPA Registry not found at {REGISTRY_PATH}: {e}")
    rpa_data = {"wilayas": {}, "matrix": {}}

class SimulationInput(BaseModel):
    total_value: float = 1837788333.0
    a_coeff: float = 0.4
    retention: float = 0.30
    degree: str = "III"
    iterations: int = 10000

@app.get("/api/portfolio/hierarchy")
def get_hierarchy():
    # Definitive hierarchy from the official Code Géographique National (2008 census)
    # with 2019 redistricting applied (wilayas 49-58).
    # 58 wilayas, 1,556 communes — each commune mapped to exactly one wilaya.
    path = os.path.join(DATA_DIR, "algeria_hierarchy.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}



# Removed static tsi_cache loading

@app.get("/api/rpa/lookup")
def lookup_rpa(wilaya: str, commune: str, group: str = "1A"):
    # Clean names
    w_name = wilaya.split(" - ")[-1].strip().upper()
    
    # Handle commune names like "147 - ROUIBA" or "ROUIBA"
    c_name = commune.upper()
    if " - " in c_name:
        c_name = c_name.split(" - ")[-1].strip()
    c_name = c_name.strip()
    
    tsi = 0.0
    premium = 0.0
    group_counts = {}

    for p in portfolio_engine.profiles:
        # Avoid pulling the entire wilaya's data if commune strings casually overlap
        pw = str(p.get("wilaya", "")).upper().split(" - ")[-1].strip()
        pc = str(p.get("commune", "")).upper().split(" - ")[-1].strip()
        
        # In the portfolio, some communes have parenthetical codes (e.g. AIN BENIAN (ALGER))
        pc_clean = pc.split("(")[0].strip().replace('-', '').replace(' ', '')
        c_clean = c_name.split("(")[0].strip().replace('-', '').replace(' ', '')
        
        # We only consider it a match if it's identical after stripping spaces/hyphens
        if w_name in pw and (pc_clean == c_clean):
            tsi += p.get("capital", 0.0)
            premium += p.get("premium", 0.0)
            t = str(p.get("type", ""))
            group_counts[t] = group_counts.get(t, 0) + 1

    w_info = rpa_data.get(w_name, {"default": "I"})
    zone = w_info.get("default", "I")
    
    # Check if commune belongs to a specific group override
    if "overrides" in w_info:
        for override_zone, communes_in_zone in w_info["overrides"].items():
            if any(c_clean == c.upper().replace('-', '').replace(' ', '') for c in communes_in_zone):
                zone = override_zone
                break
    
    # Automate Group suggestion based on portfolio "type"
    suggested_group = "2"
    suggested_vuln = "III" 
    
    if group_counts:
        top_type = max(group_counts, key=group_counts.get)
        if "Industrielle" in top_type: 
            suggested_group = "2"
            suggested_vuln = "III"
        elif "Commerciale" in top_type: 
            suggested_group = "1B"
            suggested_vuln = "II"
        else: 
            suggested_group = "2"
            suggested_vuln = "III"

    # Now calculate a_coeff using the suggested_group
    matrix = rpa_data.get("matrix", {
        "1A": {"0": 0.0, "I": 0.15, "IIa": 0.25, "IIb": 0.3, "III": 0.4},
        "1B": {"0": 0.0, "I": 0.12, "IIa": 0.2, "IIb": 0.25, "III": 0.3},
        "2": {"0": 0.0, "I": 0.1, "IIa": 0.15, "IIb": 0.2, "III": 0.25},
        "3": {"0": 0.0, "I": 0.07, "IIa": 0.1, "IIb": 0.14, "III": 0.18}
    })
    
    a_coeff = matrix.get(suggested_group, {}).get(zone, 0.10)

    return {
        "zone": zone,
        "a_coeff": a_coeff,
        "group": suggested_group,
        "vulnerability": suggested_vuln,
        "tsi": tsi,
        "premium": premium
    }

@app.post("/api/simulation/run")
def run_simulation(params: SimulationInput):
    try:
        results = monte_carlo_engine.run_simulation(
            total_value=params.total_value,
            a_coeff=params.a_coeff,
            retention_rate=params.retention,
            degree=params.degree
        )
        return results
    except Exception as e:
        return {"error": str(e)}
# ----------------- GEO DISCOVERY ENDPOINTS -----------------

@app.get("/api/geo/layers")
def list_available_layers():
    # Autonomous discovery of geospatial assets
    discovered = []
    
    # 1. Physical Files
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".geojson"):
                name = f.replace(".geojson", "").replace("_", " ").title()
                discovered.append({
                    "id": f,
                    "name": f"GIS: {name}",
                    "type": "vector",
                    "url": f"/api/geo/layer/{f}"
                })
    
    # 2. Virtual/Live Layers
    discovered.append({
        "id": "portfolio-locations",
        "name": "Live: Portfolio Concentration",
        "type": "points",
        "url": "/api/geo/locations"
    })
    
    return discovered

@app.get("/api/geo/layer/{layer_id}")
def serve_generic_layer(layer_id: str):
    path = os.path.join(DATA_DIR, layer_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Layer not found")
        
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        # Build lookup maps for automated risk coloring
        wilaya_map = {normalize_match(k): v.get("default", "I") for k, v in registry.items()}
        commune_map = {}
        for w_name, w_info in registry.items():
            if "groups" in w_info:
                for zone, communes in w_info["groups"].items():
                    for c in communes:
                        commune_map[normalize_match(c)] = zone

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for feature in data.get("features", []):
            props = feature["properties"]
            # Intelligent RPA Zone Injection
            if props.get("zone_rpa") is None:
                # Try Commune match first
                name = normalize_match(props.get("NAME") or props.get("commune") or "")
                if name in commune_map:
                    props["zone_rpa"] = commune_map[name]
                else:
                    # Fallback to Wilaya match
                    w_name = normalize_match(props.get("NAME_1") or props.get("wilaya") or "")
                    props["zone_rpa"] = wilaya_map.get(w_name, "I")
            else:
                props["zone_rpa"] = str(props["zone_rpa"])
                
        return data
    except Exception as e:
        return {"error": str(e)}

# ----------------- LEGACY GEO ENDPOINTS -----------------

def normalize_match(name: str):
    if not name: return ""
    # Strip accents and special markers
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    n = n.upper().strip()
    # Handle common abbreviations and punctuation
    n = n.replace("B.B ", "BORDJ BOU ")
    n = n.replace("B.B.", "BORDJ BOU")
    n = n.replace("O.E.B", "OUM EL BOUAGHI")
    n = n.replace("S.B.A", "SIDI BEL ABBES")
    n = n.replace("T.O", "TIZI OUZOU")
    n = n.replace("A.T", "AIN TEMOUCHENT")
    n = n.replace("A.D", "AIN DEFLA")
    n = n.replace("-", " ")
    n = n.replace(".", " ")
    # Strip double spaces
    while "  " in n: n = n.replace("  ", " ")
    return n.strip()

@app.get("/api/geo/map")
def get_geojson_wilayas():
    # Layer 1: Official Wilaya Boundaries (GADM)
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            rpa_data = json.load(f)
        map_path = os.path.join(DATA_DIR, "gadm41.geojson")
        with open(map_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for feature in data["features"]:
            props = feature["properties"]
            # Prioritize existing property if present and valid
            if props.get("zone_rpa") is not None:
                props["zone_rpa"] = str(props["zone_rpa"])
            else:
                name = normalize_match(props.get("NAME_1", ""))
                props["zone_rpa"] = rpa_data.get(name, {}).get("default", "I")
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/geo/communes")
def get_geojson_communes():
    # Layer 2: Detailed Commune Polygons (Clipped)
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            rpa_data = json.load(f)
        
        # Build global commune map for polygon injection
        commune_map = {}
        for w_name, w_info in rpa_data.items():
            if "groups" in w_info:
                for zone, communes in w_info["groups"].items():
                    for c in communes:
                        commune_map[normalize_match(c)] = zone
        
        clipped_path = os.path.join(DATA_DIR, "Clipped.geojson")
        with open(clipped_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for feature in data["features"]:
            props = feature["properties"]
            if props.get("zone_rpa") is not None:
                props["zone_rpa"] = str(props["zone_rpa"])
            else:
                name = normalize_match(props.get("NAME", ""))
                props["zone_rpa"] = commune_map.get(name, "I")
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/geo/locations")
def get_map_locations():
    # Layer 3: Portfolio Asset Points with Precision Matching
    features = []
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            rpa_data = json.load(f)
        
        # Build lookup with normalized keys
        normalized_rpa = {}
        for w_name, w_info in rpa_data.items():
            nw = normalize_match(w_name)
            normalized_rpa[nw] = { "default": w_info.get("default", "I"), "overrides": {} }
            if "groups" in w_info:
                for zone, communes in w_info["groups"].items():
                    for c in communes:
                        normalized_rpa[nw]["overrides"][normalize_match(c)] = zone
            
        for p in portfolio_engine.profiles[:12000]: # Showing more for better coverage
            if p.get("lat") and p.get("lon"):
                raw_w = str(p.get("wilaya", "")).upper().split(" - ")[-1].strip()
                raw_c = str(p.get("commune", "")).upper().split(" - ")[-1].strip()
                nw, nc = normalize_match(raw_w), normalize_match(raw_c)
                
                wilaya_entry = normalized_rpa.get(nw, {})
                zone = wilaya_entry.get("overrides", {}).get(nc, wilaya_entry.get("default", "I"))
                
                features.append({
                    "type": "Feature",
                    "geometry": { "type": "Point", "coordinates": [float(p["lon"]), float(p["lat"])] },
                    "properties": { "id": p["policy_id"], "NAME": raw_c, "zone_rpa": zone, "wilaya": raw_w }
                })
        return { "type": "FeatureCollection", "features": features }
    except Exception as e:
        return {"error": str(e)}

# ----------------- PORTFOLIO ENDPOINTS -----------------
from portfolio_engine import PortfolioEngine
from fastapi import UploadFile, File

portfolio_engine = PortfolioEngine()

@app.post("/api/portfolio/upload")
async def upload_portfolio(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    result = portfolio_engine.process_xlsx(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return result

@app.get("/api/portfolio/data")
def get_portfolio_data(offset: int = 0, limit: int = 50, sort_by: str = 'policy_id', sort_dir: str = 'asc', filter_zone: str = '', filter_verdict: str = ''):
    return portfolio_engine.get_page(offset, limit, sort_by, sort_dir, filter_zone, filter_verdict)

@app.get("/api/geo/intelligence")
def get_geo_intelligence():
    return catboost_engine.get_analytics_summary()

@app.get("/api/model/r2")
def get_model_r2():
    return {"r2": catboost_engine.r2_value if hasattr(catboost_engine, 'r2_value') else 0}

@app.get("/api/portfolio/stats")
def get_portfolio_stats():
    return portfolio_engine.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
