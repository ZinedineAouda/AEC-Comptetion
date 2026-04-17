from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from catboost_engine import engine
from portfolio_engine import portfolio_engine
import shutil
import os
import json

# --- STARTUP DATA INGESTION ---
# Auto-load from compressed cache or master XLSX if available
# Search for files in current or parent directory
def find_file(name):
    # Check current dir
    if os.path.exists(name): return name
    # Check data/
    data_path = os.path.join("data", name)
    if os.path.exists(data_path): return data_path
    # Check parent/data/
    parent_data_path = os.path.join("..", "data", name)
    if os.path.exists(parent_data_path): return parent_data_path
    # Check parent/
    parent_path = os.path.join("..", name)
    if os.path.exists(parent_path): return parent_path
    return None

MASTER_XLSX = find_file("CATNAT_2023_2025.xlsx")
CACHE_FILE = find_file("portfolio_cache.json.gz")

if CACHE_FILE:
    print(f"Initializing Portfolio Engine from compressed cache: {CACHE_FILE}")
    portfolio_engine.load_cache(CACHE_FILE)
elif MASTER_XLSX:
    print(f"Initializing Portfolio Engine from {MASTER_XLSX} (Cold Start)...")
    portfolio_engine.process_xlsx(MASTER_XLSX)
else:
    print("WARNING: No portfolio data files found!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClientRequest(BaseModel):
    property_type: str
    zone_rpa: str
    capital_assure: float
    importance_group: str = "2"
    construction_year: int = 2010
    floors: int = 1

# --- TECHNICAL REGULATORY ENGINE (CatBoost) ---

@app.post("/api/evaluate-client")
def evaluate_client(req: ClientRequest):
    result = engine.evaluate_request(
        property_type=req.property_type,
        zone_rpa=req.zone_rpa,
        capital_assure=req.capital_assure,
        importance_group=req.importance_group,
        construction_year=req.construction_year,
        floors=req.floors
    )
    return result

@app.get("/api/analytics")
def get_analytics():
    return engine.get_analytics_summary()

# --- PORTFOLIO DATABASE ENGINE ---

@app.post("/api/portfolio/upload")
async def upload_portfolio(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = portfolio_engine.process_xlsx(temp_path)
    
    try:
        os.remove(temp_path)
    except:
        pass
    
    return result

@app.get("/api/portfolio/data")
def get_portfolio_data(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("policy_id"),
    sort_dir: str = Query("asc"),
    filter_zone: str = Query(""),
    filter_verdict: str = Query("")
):
    return portfolio_engine.get_page(offset, limit, sort_by, sort_dir, filter_zone, filter_verdict)

@app.get("/api/portfolio/search")
def search_portfolio(q: str = Query("")):
    results = portfolio_engine.search(q)
    return {"results": results, "count": len(results)}

@app.get("/api/portfolio/stats")
def get_portfolio_stats():
    return portfolio_engine.get_stats()

@app.get("/api/geo/map")
def get_geo_map():
    path = find_file("gadm41.geojson")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Map file not found"}

@app.get("/api/geo/locations")
def get_geo_locations():
    path = find_file("Clipped.geojson")
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Locations file not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
