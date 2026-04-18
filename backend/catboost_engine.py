import os
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor

# RPA 99/2003 Physical Constraints & Technical Tables
RPA_LIMITS = {
    'I': 5, 
    'IIa': 4, 
    'IIb': 4, 
    'III': 3
}

# Building Importance Groups (Table 4.1) A-Coefficients baseline mapping
# This allows the AI to calibrate risk according to the official PDF
RPA_A_BASELINE = {
    '1A': 1.4, # Strategic factor
    '1B': 1.15, 
    '2':  1.0, 
    '3':  0.7  # Commercial/Limited Importance (Cheapest)
}

class InsuranceCatBoostEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(base_dir, "cleaned_portfolio_for_simulation.csv")
        # Enhanced features aligned with PDF data
        self.features = ['TYPE', 'ZONE_RPA', 'IMPORTANCE_GRP', 'CONSTRUCTION_YEAR', 'FLOORS', 'CAPITAL_ASSURE']
        self.model = CatBoostRegressor(
            iterations=150, 
            learning_rate=0.1, 
            depth=6, 
            cat_features=['TYPE', 'ZONE_RPA', 'IMPORTANCE_GRP'],
            verbose=False
        )
        self.is_trained = False
        self.df_internal = None
        self._train_baseline_model()

    def _train_baseline_model(self):
        print("Training PDF-Guided CatBoost Engine...")
        
        df = None
        # Priority 1: Processed CSV
        if os.path.exists(self.data_path):
            try:
                df = pd.read_csv(self.data_path)
                print("Loading from existing CSV...")
            except:
                pass

        # Priority 2: Fallback to master XLSX if CSV is missing
        if df is None:
            # Check root, then data/
            possible_xlsx = [
                os.path.join(os.path.dirname(self.data_path), "CATNAT_2023_2025.xlsx"),
                os.path.join(os.path.dirname(self.data_path), "data", "CATNAT_2023_2025.xlsx")
            ]
            xlsx_path = None
            for p in possible_xlsx:
                if os.path.exists(p):
                    xlsx_path = p
                    break

            if xlsx_path and os.path.exists(xlsx_path):
                try:
                    print(f"CSV missing. Training from {xlsx_path}...")
                    xl = pd.ExcelFile(xlsx_path)
                    frames = []
                    for sheet in xl.sheet_names:
                        frames.append(pd.read_excel(xl, sheet_name=sheet))
                    df = pd.concat(frames, ignore_index=True)
                    
                    # Clean columns for training
                    df.columns = df.columns.str.strip()
                    
                    # Map TYPE to internal categories
                    type_mapping = {
                        '1 - Installation Industrielle': 'Industrial',
                        '2 - Commerce': 'Commercial',
                        '3 - Habitation': 'Residential'
                    }
                    df['TYPE'] = df['TYPE'].str.strip().map(type_mapping).fillna('Residential')
                    
                    # Extract Wilaya code and Map to Zone
                    def get_zone(w_str):
                        import re
                        m = re.match(r'(\d+)', str(w_str))
                        if m:
                            code = m.group(1)
                            from portfolio_engine import WILAYA_ZONE_MAP
                            return WILAYA_ZONE_MAP.get(code, 'I')
                        return 'I'
                    
                    df['ZONE_RPA'] = df['WILAYA'].apply(get_zone)
                    
                    # Numeric parsing
                    def parse_num(v):
                        s = str(v).replace(',', '.').strip()
                        try: return float(s)
                        except: return 0.0
                    
                    df['CAPITAL_ASSURE'] = df['CAPITAL_ASSURE'].apply(parse_num)
                    df['PRIME_NETTE'] = df['PRIME_NETTE'].apply(parse_num)
                    
                except Exception as e:
                    print(f"XLSX Fallback failed: {e}")

        if df is None:
            print("No training data found (CSV or XLSX). Engine deactivated.")
            self.is_trained = False
            return

        try:
            # Map Importance Groups if missing
            if 'IMPORTANCE_GRP' not in df.columns:
                df['IMPORTANCE_GRP'] = df['TYPE'].map({
                    'Residential': '2',
                    'Commercial': '3',
                    'Industrial': '1B'
                }).fillna('2')
            
            # Synthesize missing timeline features for simulation if needed
            if 'CONSTRUCTION_YEAR' not in df.columns:
                df['CONSTRUCTION_YEAR'] = np.random.randint(1960, 2024, size=len(df))
            if 'FLOORS' not in df.columns:
                df['FLOORS'] = np.random.randint(1, 6, size=len(df))

            self.df_internal = df.copy()
            
            X = df[self.features]
            y = df['PRIME_NETTE'].abs()

            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model.fit(X_train, y_train)
            
            preds = self.model.predict(X_test)
            self.r2_value = round(r2_score(y_test, preds) * 100, 1)
            
            self.is_trained = True
            print(f"CatBoost Training Complete. R2 Score: {self.r2_value}%")
        except Exception as e:
            print(f"Error training CatBoost: {e}")
            self.is_trained = False
            self.r2_value = 0

    def evaluate_request(self, property_type: str, zone_rpa: str, capital_assure: float, 
                         importance_group: str = '2', construction_year: int = 2010, floors: int = 1):
        
        # 1. ENFORCE RPA TABLE 9.1 (RPA 99 Chapter 9)
        limit = RPA_LIMITS.get(zone_rpa, 99)
        if floors > limit:
            return {
                "status": "DECLINED",
                "reason": f"NON-COMPLIANCE: Building height ({floors} levels) exceeds the maximum limit for Zone {zone_rpa} according to RPA 99/2003 Table 9.1.",
                "estimate": None
            }

        # 2. ENFORCE CAPITAL EXPOSURE GUARD
        if zone_rpa == 'III' and capital_assure > 150000000:
            return {
                "status": "DECLINED",
                "reason": "Extreme Capital Exposure in Focal Seismic Zone (III). Structural audit required.",
                "estimate": None
            }

        if not self.is_trained:
            return {"status": "ERROR", "reason": "Model Training Required", "estimate": None}

        # 3. Predict using CatBoost (ML Layer)
        df_new = pd.DataFrame([{
            'TYPE': property_type,
            'ZONE_RPA': zone_rpa,
            'IMPORTANCE_GRP': importance_group,
            'CONSTRUCTION_YEAR': construction_year,
            'FLOORS': floors,
            'CAPITAL_ASSURE': capital_assure
        }])
        
        try:
            pred = self.model.predict(df_new)[0]
            
            # 4. Strict RPA Regulatory Multipliers (Overriding ML Anomalies)
            importance_multiplier = RPA_A_BASELINE.get(importance_group, 1.0)
            
            # Force Zone hierarchy mathematically
            zone_multipliers = {
                '0': 0.15, 'I': 0.30, 'IIa': 0.60, 'IIb': 0.80, 'III': 1.00
            }
            zone_scaling = zone_multipliers.get(zone_rpa, 0.50)
            
            # Ground truth technical baseline
            baseline = capital_assure * 0.001 * importance_multiplier * zone_scaling
            
            # Blend ML prediction with strict mathematical baseline to prevent 
            # illogical scenarios (e.g. Zone I pricing higher than Zone III)
            final_pred = (pred * 0.3) + (baseline * 0.7)
            
            # Final enforcement logic: ensure absolute baseline minimum is respected
            if final_pred < baseline:
                final_pred = baseline
            
            return {
                "status": "ACCEPTED",
                "reason": f"Risk Accepted - Importance Grp-{importance_group} calibration applied. Zone {zone_rpa} Factor strictly constrained.",
                "estimate": round(float(final_pred), 2)
            }
        except Exception as e:
            return {"status": "ERROR", "reason": str(e), "estimate": None}

    def evaluate_batch(self, df_input: pd.DataFrame):
        """ Evaluates a batch of requests for high-performance big data ingestion """
        if not self.is_trained:
            # Fallback if model not trained
            return [{"status": "ERROR", "reason": "Model Training Required", "estimate": 0.0}] * len(df_input)

        results = []
        try:
            # Apply RPA 99/2003 Table 9.1 limits
            def check_limits(row):
                limit = RPA_LIMITS.get(row['ZONE_RPA'], 99)
                if row['FLOORS'] > limit:
                    return {
                        "status": "DECLINED",
                        "reason": f"NON-COMPLIANCE: Building height ({row['FLOORS']} levels) exceeds the maximum limit for Zone {row['ZONE_RPA']} according to RPA 99/2003 Table 9.1.",
                        "estimate": None
                    }
                if row['ZONE_RPA'] == 'III' and row['CAPITAL_ASSURE'] > 150000000:
                    return {
                        "status": "DECLINED",
                        "reason": "Extreme Capital Exposure in Focal Seismic Zone (III).",
                        "estimate": None
                    }
                return None

            # Filter valid for ML predictions
            df_input['check'] = df_input.apply(check_limits, axis=1)
            valid_mask = df_input['check'].isnull()
            
            # Predict for all valid rows at once (ML vectorization)
            if valid_mask.any():
                X_batch = df_input.loc[valid_mask, self.features]
                preds = self.model.predict(X_batch)
                
                # Apply multipliers
                multipliers = df_input.loc[valid_mask, 'IMPORTANCE_GRP'].map(RPA_A_BASELINE).fillna(1.0).values
                baselines = (df_input.loc[valid_mask, 'CAPITAL_ASSURE'] * 0.0004 * multipliers).values
                final_preds = np.maximum(preds, baselines)
                
                # Fill results
                valid_idx = 0
                for i, is_valid in enumerate(valid_mask):
                    if is_valid:
                        results.append({
                            "status": "ACCEPTED",
                            "reason": f"Risk Accepted - Importance Grp calibration applied.",
                            "estimate": round(float(final_preds[valid_idx]), 2)
                        })
                        valid_idx += 1
                    else:
                        results.append(df_input.iloc[i]['check'])
            else:
                for check in df_input['check']:
                    results.append(check)
                    
            return results
        except Exception as e:
            print(f"Batch inference error: {e}")
            return [{"status": "ERROR", "reason": str(e), "estimate": 0.0}] * len(df_input)

    def get_analytics_summary(self):
        """ Returns empirical analytics computed from the dataset and model weights """
        if self.df_internal is None or self.df_internal.empty:
            return {"error": "No data available"}

        df = self.df_internal
        
        # 1. RPA Distribution from actual CSV
        if 'ZONE_RPA' in df.columns:
            zone_counts = df['ZONE_RPA'].value_counts(normalize=True).to_dict()
        else:
            zone_counts = {}

        zone_names = {
            '0': 'Zone 0 (Very Low Risk)',
            'I': 'Zone I (Low Risk)',
            'IIa': 'Zone IIa (Moderate Risk)',
            'IIb': 'Zone IIb (High Risk)',
            'III': 'Zone III (Highest Seismic Risk)'
        }
        
        rpa_distribution = {}
        for z in ['0', 'I', 'IIa', 'IIb', 'III']:
            val = zone_counts.get(z, 0)
            rpa_distribution[f"Zone {z}"] = {
                "percentage": round(val * 100, 1),
                "desc": zone_names.get(z, '')
            }

        # 2. Vulnerability / Real Exposure Risk by Type
        vulnerability_scores = []
        if 'TYPE' in df.columns and 'PRIME_NETTE' in df.columns:
            # Normalize premiums logic: higher average prime logic corresponds to higher risk
            grouped = df.groupby('TYPE')['PRIME_NETTE'].mean().abs()
            
            max_p = grouped.max() if not grouped.empty else 1
            for typ in ['Residential', 'Commercial', 'Industrial']:
                if typ in grouped:
                    score = min(round((grouped[typ] / max_p) * 100 + 10), 99) # Add 10 offset to baseline
                else:
                    score = 25 # Fallback
                
                sev = "low" if score < 40 else "medium" if score < 75 else "high"
                vulnerability_scores.append({
                    "type": typ,
                    "score": score,
                    "severity": sev,
                    "impact": "Empirical Estimate"
                })
        else:
            vulnerability_scores = [
                {"type": "Residential", "score": 25, "severity": "low", "impact": "No data"},
                {"type": "Commercial", "score": 50, "severity": "medium", "impact": "No data"},
                {"type": "Industrial", "score": 75, "severity": "high", "impact": "No data"}
            ]

        # 3. True CatBoost Feature Importance
        if self.is_trained:
            importances = self.model.get_feature_importance()
            feat_list = []
            for f_name, imp in zip(self.features, importances):
                feat_list.append({"name": f_name, "weight": round(float(imp), 1)})
            # Sort descending
            feat_list = sorted(feat_list, key=lambda x: x['weight'], reverse=True)
            
            ai_model = {
                "confidence": self.r2_value, 
                "features": feat_list
            }
        else:
            ai_model = {
                "confidence": 0,
                "features": []
            }

        return {
            "rpa_distribution": rpa_distribution,
            "vulnerability_scores": vulnerability_scores,
            "ai_model": ai_model
        }

engine = InsuranceCatBoostEngine()
