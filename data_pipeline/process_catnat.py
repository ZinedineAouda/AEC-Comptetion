"""
CATNAT Portfolio Data Processing Pipeline
Author: Elite Data Engineer (Pandas Specialist)
Description: 
This script robustly ingests, cleans, enriches, and exports insurance portfolio 
datasets. It features aggressive regex parsing for geographic codes, robust 
handling of stringified numeric features, and complex date standardization.
"""

import pandas as pd
import numpy as np
import json
import glob
import re
import os

def clean_financial_amounts(series: pd.Series) -> pd.Series:
    """
    Cleans stringified numbers containing commas and quotes.
    Transforms formats like '"1 500,000"' -> 1500.00
    """
    # Convert to string, ensuring NaNs become actual empty strings or handled properly
    s = series.astype(str)
    
    # Remove literal quotes, spaces
    s = s.str.replace(r'["\s]', '', regex=True)
    
    # Replace comma with dot for proper float casting
    s = s.str.replace(',', '.', regex=False)
    
    # Convert to numeric, coercing unparseable values to NaN, then fill with 0.0
    return pd.to_numeric(s, errors='coerce').fillna(0.0)

def standardize_types(val: str) -> str:
    """
    Normalizes mixed French categorization strings into clean English standards.
    Handles 'Bien immobilier', 'Installation Industrielle', 'Commerciale', etc.
    """
    val_lower = str(val).lower()
    if 'industri' in val_lower:
        return 'Industrial'
    elif 'commer' in val_lower:
        return 'Commercial'
    elif 'immobilier' in val_lower or 'resid' in val_lower or 'habit' in val_lower:
        return 'Residential'
    return 'Residential' # Default fallback

def get_seismic_zone(wilaya_code: str, commune_code: str) -> str:
    """
    Comprehensive mapping of all 58 Algerian Wilayas to RPA 99/2003 Seismic Zones.
    Integrates the geographic codes with the official regulatory framework limits.
    """
    try:
        w_code = str(int(wilaya_code))
    except (ValueError, TypeError):
        w_code = str(wilaya_code).strip()

    # Zone III - Sismicité Elevée
    zone_3 = ['2', '9', '16', '35', '42', '44']
    
    # Zone IIb - Sismicité Moyenne (Haute)
    zone_2b = ['6', '10', '15', '18', '19', '21', '23', '24', '25', '26', '27', '29', '31', '34', '36', '41', '43', '46', '48']
    
    # Zone IIa - Sismicité Moyenne
    zone_2a = ['4', '5', '7', '12', '13', '14', '20', '22', '38', '40']
    
    # Zone I - Sismicité Faible
    zone_1 = ['3', '17', '28', '32', '39', '45']
    
    # Zone 0 - Sismicité Négligeable (South)
    zone_0 = ['1', '8', '11', '30', '33', '37', '47', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58']
    
    if w_code in zone_3: return 'III'
    if w_code in zone_2b: return 'IIb'
    if w_code in zone_2a: return 'IIa'
    if w_code in zone_1: return 'I'
    if w_code in zone_0: return '0'

    # Complex Wilayas with commun-level splits under RPA99 (simplified to highest risk for safety)
    if w_code == '7': # Biskra split between IIa and I
        return 'IIa'
    
    return 'Unknown'

def run_pipeline():
    print("Initializing Data Pipeline...")

    # 1. DATA INGESTION
    csv_files = glob.glob('CATNAT_*.csv')
    excel_files = glob.glob('CATNAT_*.xlsx')
    
    all_files = csv_files + excel_files
    if not all_files:
        print("CRITICAL ERROR: No CATNAT CSV or XLSX files found in the current directory.")
        return

    dataframes = []
    for file in all_files:
        try:
            print(f"Loading {file}...")
            # Enforce string types on geo columns during read
            if file.endswith('.csv'):
                df_temp = pd.read_csv(file, dtype={'WILAYA': str, 'COMMUNE': str, 'TYPE': str})
            else:
                df_temp = pd.read_excel(file, dtype={'WILAYA': str, 'COMMUNE': str, 'TYPE': str})
            dataframes.append(df_temp)
        except Exception as e:
            print(f"ERROR: Failed to load {file}. Details: {e}")
            continue

    if not dataframes:
        print("CRITICAL ERROR: No valid data could be aggregated. Exiting.")
        return

    df = pd.concat(dataframes, ignore_index=True)
    print(f"Aggregated {len(df)} total records. Commencing cleaning...")

    # 2. NUMERIC FORMATTING (PRIME_NETTE & CAPITAL_ASSURE)
    if 'CAPITAL_ASSURE' in df.columns:
        df['CAPITAL_ASSURE'] = clean_financial_amounts(df['CAPITAL_ASSURE'])
    if 'PRIME_NETTE' in df.columns:
        df['PRIME_NETTE'] = clean_financial_amounts(df['PRIME_NETTE'])

    # 3. CATEGORICAL STANDARDIZATION (TYPE)
    if 'TYPE' in df.columns:
        df['TYPE_CLEAN'] = df['TYPE'].apply(standardize_types)

    # 4. GEOGRAPHIC STRING MIXING (WILAYA & COMMUNE)
    # Using strict regex extraction: ^(\d+)\s*[-_]?\s*(.*)$
    # This grabs leading digits as the code, and anything following (optional dashes) as the name
    wilaya_pattern = r'^(?P<WILAYA_CODE>\d+)\s*[-_]?\s*(?P<WILAYA_NAME>.*)$'
    if 'WILAYA' in df.columns:
        extracted_w = df['WILAYA'].str.extract(wilaya_pattern)
        # For rows that don't match the regex (e.g. just text "ALGER"), the code might be NaN
        df['WILAYA_CODE'] = extracted_w['WILAYA_CODE'].fillna('Unknown')
        df['WILAYA_NAME'] = extracted_w['WILAYA_NAME'].replace('', np.nan).fillna(df['WILAYA']).str.strip()

    commune_pattern = r'^(?P<COMMUNE_CODE>\d+)\s*[-_]?\s*(?P<COMMUNE_NAME>.*)$'
    if 'COMMUNE' in df.columns:
        extracted_c = df['COMMUNE'].str.extract(commune_pattern)
        df['COMMUNE_CODE'] = extracted_c['COMMUNE_CODE'].fillna('Unknown')
        df['COMMUNE_NAME'] = extracted_c['COMMUNE_NAME'].replace('', np.nan).fillna(df['COMMUNE']).str.strip()

    # 5. DATES PARSING
    # Attempt parsing with format='mixed' and dayfirst logic to handle ambiguous DD/MM/YYYY vs YYYY-MM-DD
    print("Normalizing date vectors...")
    if 'DATE_EFFET' in df.columns:
        df['DATE_EFFET'] = pd.to_datetime(df['DATE_EFFET'], format='mixed', dayfirst=True, errors='coerce')
    if 'DATE_EXPIRATION' in df.columns:
        df['DATE_EXPIRATION'] = pd.to_datetime(df['DATE_EXPIRATION'], format='mixed', dayfirst=True, errors='coerce')

    # Convert datetimes directly back to strict YYYY-MM-DD string representations for output formats
    df['DATE_EFFET_STR'] = df['DATE_EFFET'].dt.strftime('%Y-%m-%d').fillna('')
    df['DATE_EXPIRATION_STR'] = df['DATE_EXPIRATION'].dt.strftime('%Y-%m-%d').fillna('')

    # 6. RPA SEISMIC ZONING 
    print("Executing RPA Seismic logic mappings...")
    df['ZONE_RPA'] = df.apply(lambda row: get_seismic_zone(row.get('WILAYA_CODE', ''), row.get('COMMUNE_CODE', '')), axis=1)

    # 7. OUTPUT GENERATION
    # Selecting the exact cleaned columns specified
    export_columns = [
        'NUMERO_POLICE', 'CODE_SOUS_BRANCHE', 'NUM_AVNT_COURS', 
        'DATE_EFFET_STR', 'DATE_EXPIRATION_STR', 'TYPE_CLEAN', 
        'WILAYA_CODE', 'WILAYA_NAME', 'COMMUNE_CODE', 'COMMUNE_NAME', 
        'CAPITAL_ASSURE', 'PRIME_NETTE', 'ZONE_RPA'
    ]
    
    # Ensure no missing columns crash the export
    available_export_cols = [col for col in export_columns if col in df.columns]
    final_df = df[available_export_cols].copy()

    # Rename the date string columns back to standard for the output
    final_df.rename(columns={
        'DATE_EFFET_STR': 'DATE_EFFET', 
        'DATE_EXPIRATION_STR': 'DATE_EXPIRATION',
        'TYPE_CLEAN': 'TYPE'
    }, inplace=True)

    print("Generating simulated CSV output...")
    try:
        final_df.to_csv('cleaned_portfolio_for_simulation.csv', index=False, encoding='utf-8')
        print(" > Successfully saved: cleaned_portfolio_for_simulation.csv")
    except Exception as e:
        print(f"ERROR saving CSV: {e}")

    print("Generating Frontend JSON output...")
    try:
        # orient='records' exports arrays of objects correctly as demanded by React/JS frontends
        final_df.to_json('processed_portfolio.json', orient='records', indent=2, force_ascii=False)
        print(" > Successfully saved: processed_portfolio.json")
    except Exception as e:
        print(f"ERROR saving JSON: {e}")

    print("Pipeline Execution Completed Successfully.")

if __name__ == "__main__":
    run_pipeline()
