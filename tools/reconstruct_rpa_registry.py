import json
import os
import unicodedata
import sys
import difflib

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_match(name: str):
    if not name: return ""
    n = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('utf-8')
    n = n.upper().strip().replace("-", " ").replace(".", " ").replace("_", " ")
    while "  " in n: n = n.replace("  ", " ")
    return n.strip()

def build_master_registry():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    HIERARCHY_PATH = os.path.join(DATA_DIR, "algeria_hierarchy.json")
    PDF_TEXT_PATH = os.path.join(DATA_DIR, "..", "docs", "pdf_extracted_text.txt")
    OUTPUT_PATH = os.path.join(DATA_DIR, "seismic_registry_rpa.json")

    print(f"Loading Hierarchy...")
    with open(HIERARCHY_PATH, "r", encoding="utf-8") as f:
        hierarchy = json.load(f)

    # Simplified hierarchy map for fuzzy matching
    h_wilayas = {}
    for k, communes in hierarchy.items():
        w_name = normalize_match(k.split("-")[-1])
        h_wilayas[w_name] = [normalize_match(c) for c in communes]

    print(f"Loading PDF Text...")
    with open(PDF_TEXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Manual extraction based on careful audit of the desynced text lines
    # Structure: Wilaya Name -> {GroupA_Zone, GroupB_Zone, GroupC_Zone}
    # And Group definitions.
    
    # This is a refined map of the 48 historical Wilayas with their RPA 2003 zones
    # Based on the pdf_extracted_text audit (Lines 600-1029)
    
    registry = {}

    def add_wilaya(name, default_zone, groups=None):
        registry[name] = {
            "default": default_zone,
            "groups": groups or {}
        }

    # ADRAR (01) - Zone 0
    add_wilaya("ADRAR", "0")
    
    # CHLEF (02) - III (Default), IIb (B), IIa (C)
    add_wilaya("CHLEF", "III", {
        "IIb": ["EL KARIMIA", "EL HARCHOUN", "SENDJAS", "OUED SLY", "BOUKADIR"],
        "IIa": ["OULED BEN AEK", "EL HADJADJ"]
    })
    
    # LAGHOUAT (03) - I
    add_wilaya("LAGHOUAT", "I")
    
    # OUM EL BOUAGHI (04) - I
    add_wilaya("OUM EL BOUAGHI", "I")
    
    # BATNA (05) - I
    add_wilaya("BATNA", "I")
    
    # BEJAIA (06) - IIa
    add_wilaya("BEJAIA", "IIa")
    
    # BISKRA (07) - I
    add_wilaya("BISKRA", "I")
    
    # BECHAR (08) - 0
    add_wilaya("BECHAR", "0")
    
    # BLIDA (09) - III (Default), IIb (B)
    add_wilaya("BLIDA", "III", {
        "IIb": ["MEFTAH", "DJEBABRA", "SOUHANE", "LARBAA", "OULED SLAMA", "BOUGARA", "HAMMAM MELOUANE", "AIN ROMANA"]
    })
    
    # BOUIRA (10) - IIa
    add_wilaya("BOUIRA", "IIa")
    
    # TAMANRASSET (11) - 0
    add_wilaya("TAMANRASSET", "0")
    
    # TEBESSA (12) - I
    add_wilaya("TEBESSA", "I")
    
    # TLEMCEN (13) - I
    add_wilaya("TLEMCEN", "I")
    
    # TIARET (14) - I
    add_wilaya("TIARET", "I")
    
    # TIZI OUZOU (15) - IIa (Default), IIb (Mizrana)
    add_wilaya("TIZI OUZOU", "IIa", {
        "IIb": ["MIZRANA"]
    })
    
    # ALGER (16) - III
    add_wilaya("ALGER", "III")
    
    # DJELFA (17) - I
    add_wilaya("DJELFA", "I")
    
    # JIJEL (18) - IIa
    add_wilaya("JIJEL", "IIa")
    
    # SETIF (19) - IIa
    add_wilaya("SETIF", "IIa")
    
    # SAIDA (20) - I
    add_wilaya("SAIDA", "I")
    
    # SKIKDA (21) - IIa
    add_wilaya("SKIKDA", "IIa")
    
    # SIDI BEL ABBES (22) - I
    add_wilaya("SIDI BEL ABBES", "I")
    
    # ANNABA (23) - IIa
    add_wilaya("ANNABA", "IIa")
    
    # GUELMA (24) - IIa
    add_wilaya("GUELMA", "IIa")
    
    # CONSTANTINE (25) - IIa
    add_wilaya("CONSTANTINE", "IIa")
    
    # MEDEA (26) - IIa (Default), III (A), IIb (B)
    add_wilaya("MEDEA", "IIa", {
        "III": ["EL HAMDANIA", "MEDEA", "TAMESGUIDA"],
        "IIb": ["DRAA ISMAIL", "SI MANSOUR", "BEN CHIKHAO", "EL OMARIA", "OULED HELLAL", "OULED DEIDE", "BOUAICHE", "CHAHBOUNIA", "BOUGHEZOUL", "SANEG", "MEFTAHA", "OULED MAREF", "EL OUINET", "AIN BOUCIF", "SIDI DAMED", "AIN OUKSIR", "CHENIGUEL"]
    })
    
    # MOSTAGANEM (27) - IIa (Default), III (A), IIb (B)
    add_wilaya("MOSTAGANEM", "IIa", {
        "III": ["OULED BOUGHALEM", "ACHAACHA", "KHADRA", "NEKMARIA"],
        "IIb": ["SIDI LAKHDAR", "TAZGAIT", "OULED MAALEF"]
    })
    
    # MSILA (28) - I (Default), IIa (A) - Matches user screenshot!
    add_wilaya("M'SILA", "I", {
        "IIa": ["BENI ILMANE", "OUANOUGHA", "HAMMAM DHALAA", "TARMOUNT", "OULED MANSOUR", "M'SILA", "MTARFA", "MAADID", "OULED DERRADJ", "OULED ADDI GUEBALA", "DEHAHNA", "BERHOUM", "AIN KHADRA", "MAGRA", "BELAIBA"]
    })
    
    # MASCARA (29) - IIa (Default), I (B)
    add_wilaya("MASCARA", "IIa", {
        "I": ["AIN FARES", "AIN FEKAN", "BOU HANIFIA", "GUERDJOUM", "OUED TARIA", "GHRISS", "BENIAN", "MAKDHA", "AOUF", "GHARROUS", "NESMOT", "EL HACHEM", "OUED EL ABTAL", "AIN FERAH"]
    })
    
    # OUARGLA (30) - 0
    add_wilaya("OUARGLA", "0")
    
    # ORAN (31) - IIa
    add_wilaya("ORAN", "IIa")
    
    # EL BAYADH (32) - I
    add_wilaya("EL BAYADH", "I")
    
    # ILLIZI (33) - 0
    add_wilaya("ILLIZI", "0")
    
    # BORDJ BOU ARRERIDJ (34) - IIa
    add_wilaya("BORDJ BOU ARRERIDJ", "IIa")
    
    # BOUMERDES (35) - III (Default), IIb (B), IIa (C)
    add_wilaya("BOUMERDES", "III", {
        "IIb": ["AFIR", "BENCHOUD", "TAOURGA", "BAGHLIA", "OULED AISSA", "NACIRIA", "BORDJ MENAIEL", "ISSER", "BENI AMRANE", "SOUK EL HAD", "BOUZEGZA KEDARA", "EL KHARROUBA", "LARBATACHE", "KHEMIS EL KHECHNA", "OULED MOUSSA", "HAMMEDI"],
        "IIa": ["TIMEZRIT", "AMMAL", "CHAABET EL AMEUR"]
    })
    
    # EL TARF (36) - IIa
    add_wilaya("EL TARF", "IIa")
    
    # TINDOUF (37) - 0
    add_wilaya("TINDOUF", "0")
    
    # TISSEMSILT (38) - IIa
    add_wilaya("TISSEMSILT", "IIa")
    
    # EL OUED (39) - 0
    add_wilaya("EL OUED", "0")
    
    # KHENCHELA (40) - I
    add_wilaya("KHENCHELA", "I")
    
    # SOUK AHRAS (41) - I
    add_wilaya("SOUK AHRAS", "I")
    
    # TIPAZA (42) - III
    add_wilaya("TIPAZA", "III")
    
    # MILA (43) - IIa
    add_wilaya("MILA", "IIa")
    
    # AIN DEFLA (44) - IIa (Default), III (A), IIb (B)
    add_wilaya("AIN DEFLA", "IIa", {
        "III": ["TACHETA ZEGAGHA", "EL ABADIA", "AIN BOUYAHIA", "EL ATTAF"],
        "IIb": ["EL AMRA", "MEKHATRIA", "ARIB", "ROUINA", "AIN DEFLA", "BOURACHED", "ZEDDINE", "TIBERKANINE", "MILIANA", "AIN TORKI", "HAMMAM RIGHA", "AIN BENIAN", "HOCEINIA", "BOU MEDFAA"]
    })
    
    # NAAMA (45) - I
    add_wilaya("NAAMA", "I")
    
    # AIN TEMOUCHENT (46) - IIa
    add_wilaya("AIN TEMOUCHENT", "IIa")
    
    # GHARDAIA (47) - 0
    add_wilaya("GHARDAIA", "0")
    
    # RELIZANE (48) - IIa (Default), III (A), IIb (B)
    add_wilaya("RELIZANE", "IIa", {
        "III": ["MEDIOUNA", "SIDI M'HAMED BEN ALI", "MAZOUNA", "EL GUETTAR"],
        "IIb": ["MERDJA SIDI ABED", "OUED RHIOU", "OUARIZANE", "DJIDIOUIA", "EL HAMRI", "BENI ZENTIS"]
    })

    # New Wilayas (49-58) inherit from parents (simplified for this task)
    new_wilayas = {
        "EL M'GHAIER": "EL OUED", "EL MENIAA": "GHARDAIA", "OULED DJELLAL": "BISKRA", 
        "BORDJ BADJI MOKHTAR": "ADRAR", "BENI ABBES": "BECHAR", "TIMIMOUN": "ADRAR",
        "TOUGGOURT": "OUARGLA", "DJANET": "ILLIZI", "IN SALAH": "TAMANRASSET", "IN GUEZZAM": "TAMANRASSET"
    }
    for new_w, parent in new_wilayas.items():
        if parent in registry:
            registry[new_w] = registry[parent]

    print(f"Final Audit: Syncing naming with hierarchy...")
    # This step ensures that all names in the registry match the official hierarchy spelling.
    # If a name doesn't match, we use fuzzy matching to find the closest hierarchy equivalent.
    
    final_registry = {}
    for w_name, w_info in registry.items():
        nw_name = normalize_match(w_name)
        # Find wilaya key in hierarchy
        h_w_key = next((k for k in hierarchy.keys() if normalize_match(k.split("-")[-1]) == nw_name), None)
        
        if not h_w_key:
            print(f"Warning: Wilaya {w_name} not found in hierarchy.")
            final_registry[w_name] = w_info
            continue
            
        h_communes = [normalize_match(c) for c in hierarchy[h_w_key]]
        
        new_groups = {}
        for zone, communes in w_info.get("groups", {}).items():
            new_list = []
            for c in communes:
                nc = normalize_match(c)
                if nc in h_communes:
                    new_list.append(c) # Keep original but it matches
                else:
                    # Fuzzy match within this wilaya
                    match = difflib.get_close_matches(nc, h_communes, n=1, cutoff=0.7)
                    if match:
                        # Find original casing in hierarchy
                        idx = h_communes.index(match[0])
                        new_list.append(hierarchy[h_w_key][idx])
                    else:
                        print(f"Warning: Commune {c} in {w_name} has no good match in hierarchy.")
                        new_list.append(c)
            new_groups[zone] = new_list
            
        final_registry[h_w_key.split("-")[-1].strip().upper()] = {
            "default": w_info["default"],
            "groups": new_groups
        }

    print(f"Saving Reconstructed Registry...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_registry, f, indent=4)
    print("Success!")

if __name__ == "__main__":
    build_master_registry()
