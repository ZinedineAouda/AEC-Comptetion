import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json
import re
import os
from datetime import datetime

# RPA 99/2003 Zone Mapping for communes (wilaya code -> zone)
WILAYA_ZONE_MAP = {
    '2': 'III', '9': 'IIb', '35': 'III', '15': 'IIb', '10': 'IIb',
    '26': 'IIa', '6': 'IIb', '16': 'III', '42': 'III', '36': 'IIa',
    '25': 'IIa', '5': 'IIa', '19': 'IIa', '34': 'IIa', '43': 'IIa',
    '23': 'IIa', '21': 'IIa', '18': 'IIa', '4': 'IIa', '44': 'IIb',
    '28': 'IIa', '29': 'IIa', '27': 'I', '22': 'I', '7': 'I',
    '48': 'I', '12': 'I', '14': 'I', '46': 'I', '20': 'I',
    '24': 'I', '13': 'I', '17': 'I', '38': 'I', '40': 'I',
    '31': 'IIa', '30': 'I', '45': 'I', '47': 'I', '8': 'I',
    '11': '0', '33': '0', '39': '0', '37': '0', '41': '0',
    '3': '0', '32': '0', '1': '0',
}

ZONE_RATE = {'0': 0.00045, 'I': 0.00075, 'IIa': 0.0015, 'IIb': 0.002, 'III': 0.003}
TYPE_MULTIPLIER = {'1': 1.50, '2': 1.25, '3': 1.00}  # Industrial, Commercial, Residential

class PortfolioEngine:
    """Processes CATNAT XLSX files with deduplication, pricing validation, and search."""
    
    def __init__(self):
        self.profiles: List[Dict[str, Any]] = []
        self.raw_count = 0
        self.load_cache()
    
    def _extract_wilaya_code(self, wilaya_str: str) -> str:
        """Extract numeric wilaya code from '16 - ALGER' format."""
        match = re.match(r'(\d+)', str(wilaya_str).strip())
        return match.group(1) if match else '0'
    
    def _extract_type_code(self, type_str: str) -> str:
        """Extract type code from '1 - Installation Industrielle'."""
        match = re.match(r'(\d+)', str(type_str).strip())
        return match.group(1) if match else '3'
    
    def _parse_number(self, val) -> float:
        """Parse European-format numbers like '2500,000' or standard floats."""
        if pd.isna(val):
            return 0.0
        s = str(val).strip()
        # Handle European comma decimal: '2500,000' -> 2500.0
        if ',' in s and '.' not in s:
            s = s.replace(',', '.')
        try:
            return float(s)
        except ValueError:
            return 0.0
    
    def _compute_fair_premium(self, capital: float, wilaya_code: str, type_code: str) -> float:
        """Compute the RPA-compliant fair premium based on zone, capital, and property type."""
        zone = WILAYA_ZONE_MAP.get(wilaya_code, 'I')
        rate = ZONE_RATE.get(zone, 0.00075)
        tmul = TYPE_MULTIPLIER.get(type_code, 1.0)
        return round(capital * rate * tmul, 2)
    
    def _assess_pricing(self, actual: float, fair: float) -> Dict:
        """Evaluate the deal quality by comparing actual vs fair premium."""
        if fair <= 0:
            return {"verdict": "NO_DATA", "ratio": 0, "label": "Insufficient Data", "color": "gray"}
        
        ratio = actual / fair
        
        if ratio < 0.5:
            return {"verdict": "SEVERELY_UNDERPRICED", "ratio": round(ratio, 2), 
                    "label": f"Underpriced ({round(ratio*100)}% of fair value)", "color": "red"}
        elif ratio < 0.85:
            return {"verdict": "UNDERPRICED", "ratio": round(ratio, 2),
                    "label": f"Below Market ({round(ratio*100)}%)", "color": "orange"}
        elif ratio <= 1.15:
            return {"verdict": "FAIR", "ratio": round(ratio, 2),
                    "label": f"Fair Price ({round(ratio*100)}%)", "color": "green"}
        elif ratio <= 1.5:
            return {"verdict": "PROFITABLE", "ratio": round(ratio, 2),
                    "label": f"Profitable ({round(ratio*100)}%)", "color": "blue"}
        else:
            return {"verdict": "OVERPRICED", "ratio": round(ratio, 2),
                    "label": f"Premium ({round(ratio*100)}%)", "color": "purple"}
    
    def load_cache(self, cache_path: str = None):
        """Load processed profiles from disk if available."""
        if cache_path is None:
            # Check standard locations
            for p in ["data/portfolio_cache.json.gz", "../data/portfolio_cache.json.gz", "portfolio_cache.json.gz", "../portfolio_cache.json.gz"]:
                if os.path.exists(p):
                    cache_path = p
                    break
        
        if cache_path and os.path.exists(cache_path):
            import gzip
            try:
                with gzip.open(cache_path, 'rb') as f:
                    data = json.load(f)
                    self.profiles = data.get("profiles", [])
                    print(f"Loaded {len(self.profiles)} profiles from cache.")
                    return True
            except Exception as e:
                print(f"Cache load error: {e}")
        return False

    def save_cache(self, cache_path: str = None):
        """Save current profiles to disk using gzip compression."""
        if cache_path is None:
            # Default to data/ if it exists, otherwise use root or parent data
            if os.path.exists("data"):
                cache_path = "data/portfolio_cache.json.gz"
            elif os.path.exists("../data"):
                cache_path = "../data/portfolio_cache.json.gz"
            else:
                cache_path = "portfolio_cache.json.gz"
        
        import gzip
        data = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "profile_count": len(self.profiles)
            },
            "profiles": self.profiles
        }
        try:
            temp_path = cache_path + ".tmp"
            with gzip.open(temp_path, 'wb') as f:
                f.write(json.dumps(data).encode('utf-8'))
            if os.path.exists(cache_path):
                os.remove(cache_path)
            os.rename(temp_path, cache_path)
            print(f"Saved {len(self.profiles)} profiles to compressed cache.")
        except Exception as e:
            print(f"Cache save error: {e}")

    def process_xlsx(self, file_path: str, use_cache: bool = True) -> Dict:
        """Optimized pipeline using vectorization and caching."""
        print(f"Starting ingestion for: {file_path}")
        try:
            xl = pd.ExcelFile(file_path)
            print(f"Excel loaded. Sheets: {xl.sheet_names}")
            all_rows = []
            
            for sheet in xl.sheet_names:
                print(f"Reading sheet: {sheet}...")
                df = pd.read_excel(xl, sheet_name=sheet)
                print(f"  Got {len(df)} rows.")
                df['_sheet'] = sheet
                all_rows.append(df)
            
            combined = pd.concat(all_rows, ignore_index=True)
            self.raw_count = len(combined)
            print(f"Combined total: {self.raw_count} rows.")
            
            # --- Vectorized Cleaning ---
            print("Cleaning data (vectorized)...")
            combined['NUMERO_POLICE'] = combined['NUMERO_POLICE'].astype(str).str.strip()
            # Filter out empty or total rows
            combined = combined[combined['NUMERO_POLICE'].str.len() > 3]
            
            combined['_wilaya_code'] = combined['WILAYA'].apply(self._extract_wilaya_code)
            combined['_type_code'] = combined['TYPE'].apply(self._extract_type_code)
            combined['_cap_num'] = combined['CAPITAL_ASSURE'].apply(self._parse_number)
            combined['_price_num'] = combined['PRIME_NETTE'].apply(self._parse_number)
            
            # 2. Get Base and Latest records (Vectorized)
            print("Identifying unique policies...")
            base_df = combined.drop_duplicates('NUMERO_POLICE', keep='first').set_index('NUMERO_POLICE')
            latest_df = combined.drop_duplicates('NUMERO_POLICE', keep='last').set_index('NUMERO_POLICE')
            print(f"Unique policies identified: {len(latest_df)}")

            # 3. Vectorized Fair Premium Calculation
            print("Calculating fair premiums...")
            def vector_fair(row):
                return self._compute_fair_premium(
                    row['_cap_num'], 
                    row['_wilaya_code'],
                    row['_type_code']
                )

            latest_df['fair_premium'] = latest_df.apply(vector_fair, axis=1)
            
            # 4. High-Performance Revisions Aggregation
            print("Building revision histories...")
            # Convert dates to string here to avoid Timestamp serialization errors
            rev_df = combined[[
                'NUMERO_POLICE', 'NUM_AVNT_COURS', 'DATE_EFFET', 
                'DATE_EXPIRATION', '_cap_num', '_price_num', '_sheet'
            ]].copy()
            rev_df['DATE_EFFET'] = rev_df['DATE_EFFET'].astype(str)
            rev_df['DATE_EXPIRATION'] = rev_df['DATE_EXPIRATION'].astype(str)
            
            records = rev_df.rename(columns={
                'NUMERO_POLICE': 'pid', 'NUM_AVNT_COURS': 'avenant', 
                'DATE_EFFET': 'date_effet', 'DATE_EXPIRATION': 'date_expiration', 
                '_cap_num': 'capital', '_price_num': 'premium', '_sheet': 'year'
            }).to_dict('records')
            
            rev_map = {}
            for r in records:
                pid = r.pop('pid')
                if pid not in rev_map: rev_map[pid] = []
                rev_map[pid].append(r)

            # 5. Build Final Profiles
            print("Assembling final profiles...")
            final_profiles = []
            for pid, row in latest_df.iterrows():
                base = base_df.loc[pid]
                assessment = self._assess_pricing(row['_price_num'], row['fair_premium'])
                
                final_profiles.append({
                    "policy_id": str(pid),
                    "branch_code": str(base.get('CODE_SOUS_BRANCHE', '')),
                    "type": str(base.get('TYPE', 'Unknown')),
                    "wilaya": str(base.get('WILAYA', 'Unknown')),
                    "commune": str(base.get('COMMUNE', 'Unknown')),
                    "zone_rpa": WILAYA_ZONE_MAP.get(row['_wilaya_code'], 'I'),
                    "capital": float(row['_cap_num']),
                    "premium": float(row['_price_num']),
                    "fair_premium": float(row['fair_premium']),
                    "date_effet": str(base.get('DATE_EFFET', '')),
                    "date_expiration": str(base.get('DATE_EXPIRATION', '')),
                    "revisions": rev_map.get(pid, []),
                    "revision_count": len(rev_map.get(pid, [])),
                    "assessment": assessment
                })
            
            # Merge final_profiles into self.profiles by policy_id
            existing_profiles = {p['policy_id']: p for p in self.profiles}
            for new_p in final_profiles:
                existing_profiles[new_p['policy_id']] = new_p
            self.profiles = list(existing_profiles.values())
            
            print(f"Profiles assembled: {len(self.profiles)}. Saving to cache...")
            
            # Atomic Save
            self.save_cache()
            print("Ingestion complete.")
            
            return {
                "status": "success",
                "source": "xlsx",
                "raw_records": self.raw_count,
                "unique_policies": len(self.profiles)
            }
        except Exception as e:
            print(f"FATAL INGESTION ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def search(self, query: str) -> List[Dict]:
        """Smart search with caching support."""
        q = query.lower().strip()
        if not q:
            return self.profiles[:100]
        return [p for p in self.profiles if 
                q in p['policy_id'].lower() or 
                q in p['wilaya'].lower() or 
                q in p['commune'].lower()][:200]
    
    def get_page(self, offset: int = 0, limit: int = 50, 
                 sort_by: str = 'policy_id', sort_dir: str = 'asc',
                 filter_zone: str = '', filter_verdict: str = '') -> Dict:
        """Paginated, sorted, filtered access."""
        data = self.profiles
        
        # Application of filters
        if filter_zone:
            data = [p for p in data if p['zone_rpa'] == filter_zone]
        if filter_verdict:
            data = [p for p in data if p['assessment']['verdict'] == filter_verdict]
        
        # Sort logic
        reverse = sort_dir == 'desc'
        try:
            if sort_by in ('capital', 'premium', 'fair_premium'):
                data = sorted(data, key=lambda x: x.get(sort_by, 0), reverse=reverse)
            elif sort_by == 'ratio':
                data = sorted(data, key=lambda x: x['assessment'].get('ratio', 0), reverse=reverse)
            else:
                data = sorted(data, key=lambda x: str(x.get(sort_by, '')), reverse=reverse)
        except:
            pass
        
        total = len(data)
        page = data[offset:offset+limit]
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": page
        }
    
    def get_stats(self) -> Dict:
        """Dashboard summary statistics."""
        if not self.profiles:
            return { "total_policies": 0, "total_capital": 0, "total_premium": 0, "by_verdict": {}, "by_zone": {} }
        
        verdicts = {}
        zones = {}
        total_capital = 0
        total_premium = 0
        for p in self.profiles:
            v = p['assessment']['verdict']
            verdicts[v] = verdicts.get(v, 0) + 1
            z = p['zone_rpa']
            zones[z] = zones.get(z, 0) + 1
            total_capital += p['capital']
            total_premium += p['premium']
        
        return {
            "total_policies": len(self.profiles),
            "total_capital": round(total_capital, 2),
            "total_premium": round(total_premium, 2),
            "by_verdict": verdicts,
            "by_zone": zones
        }

portfolio_engine = PortfolioEngine()
