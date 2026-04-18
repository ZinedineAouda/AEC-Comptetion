# Comprehensive Algerian Wilayas and Communes Database
OFFICIAL_WILAYAS = {
    "01": "ADRAR", "02": "CHLEF", "03": "LAGHOUAT", "04": "OUM EL BOUAGHI", "05": "BATNA",
    "06": "BEJAIA", "07": "BISKRA", "08": "BECHAR", "09": "BLIDA", "10": "BOUIRA",
    "11": "TAMANRASSET", "12": "TEBESSA", "13": "TLEMCEN", "14": "TIARET", "15": "TIZI OUZOU",
    "16": "ALGER", "17": "DJELFA", "18": "JIJEL", "19": "SETIF", "20": "SAIDA",
    "21": "SKIKDA", "22": "SIDI BEL ABBES", "23": "ANNABA", "24": "GUELMA", "25": "CONSTANTINE",
    "26": "MEDEA", "27": "MOSTAGANEM", "28": "M'SILA", "29": "MASCARA", "30": "OUARGLA",
    "31": "ORAN", "32": "EL BAYADH", "33": "ILLIZI", "34": "BORDJ BOU ARRERIDJ", "35": "BOUMERDES",
    "36": "EL TARF", "37": "TINDOUF", "38": "TISSEMSILT", "39": "EL OUED", "40": "KHENCHELA",
    "41": "SOUK AHRAS", "42": "TIPAZA", "43": "MILA", "44": "AIN DEFLA", "45": "NAAMA",
    "46": "AIN TEMOUCHENT", "47": "GHARDAIA", "48": "RELIZANE", "49": "TIMIMOUN", "50": "BORDJ BADJI MOKHTAR",
    "51": "OULED DJELLAL", "52": "BENI ABBES", "53": "IN SALAH", "54": "IN GUEZZAM", "55": "TOUGGOURT",
    "56": "DJANET", "57": "EL M'GHAIER", "58": "EL MENIAA"
}

# Extensive mapping of communes
# (This is a simplified large-scale representation to ensure all wilayas have data)
CORE_COMMUNES = {
    "01": ["ADRAR", "REGGANE", "TIMIMOUN", "FENOUGHIL", "AOULEF"],
    "02": ["CHLEF", "OUED FODDA", "TENES", "MOUSSADEK", "BOUKADIR"],
    "03": ["LAGHOUAT", "AFLOU", "AIN MADHI", "HASSI R'MEL"],
    "04": ["OUM EL BOUAGHI", "AIN BEIDA", "AIN M'LILA", "MESKIANA"],
    "05": ["BATNA", "ARRIS", "BARIKA", "MEROUANA", "N'GAOUS"],
    "06": ["BEJAIA", "AKBOU", "EL KSEUR", "AMIZOUR", "TIMEZRIT"],
    "07": ["BISKRA", "TOLGA", "OULED DJELLAL", "SIDI OKBA"],
    "08": ["BECHAR", "KENADSA", "TAGHIT", "BENI ABBES"],
    "09": ["BLIDA", "BOUFARIK", "LARBAA", "OUED ALLEUG", "MOUZAIA"],
    "10": ["BOUIRA", "LAKHDARIA", "SOUR EL GHOZLANE", "AIN BESSEM"],
    "11": ["TAMANRASSET", "IN SALAH", "IN GUEZZAM", "IDLES"],
    "12": ["TEBESSA", "BIR EL ATER", "CHERIA", "OUENZA"],
    "13": ["TLEMCEN", "MAGHNIA", "GHAZAOUET", "REMMCHI", "NEDROMA"],
    "14": ["TIARET", "SOUGUEUR", "FRENDA", "KSAR CHELLALA"],
    "15": ["TIZI OUZOU", "AZAZGA", "DRAA EL MIZAN", "LARBAA NATH IRATHEN"],
    "16": ["ALGER", "ROUIBA", "BAB EL OUED", "EL HARRACH", "ZERALDA", "REGHAIA", "BIR MOURAD RAIS", "KOUBA", "HYDRA"],
    "17": ["DJELFA", "HASSI BAHBAH", "MESSAAD", "AIN OUSSERA"],
    "18": ["JIJEL", "TAHER", "EL MILIA", "SETARA"],
    "19": ["SETIF", "EL EULMA", "AIN OULMENE", "AIN ARNAT"],
    "20": ["SAIDA", "YOUB", "HASSASNA"],
    "21": ["SKIKDA", "COLLO", "AZZABA", "EL HARROUCH"],
    "22": ["SIDI BEL ABBES", "TESSALA", "SFISEF", "TELAGH"],
    "23": ["ANNABA", "EL BOUNI", "BERRAHAL", "EL HADJAR"],
    "24": ["GUELMA", "BOUCHEGOUF", "HELIOPOLIS", "OUED ZENATI"],
    "25": ["CONSTANTINE", "EL KHROUB", "HAMMA BOUZIANE", "DIDOUCHE MOURAD"],
    "26": ["MEDEA", "KSAR EL BOUKHARI", "BENI SLIMANE", "BERROUAGHIA"],
    "27": ["MOSTAGANEM", "HASSI MAMECHE", "SIDI LAKHDAR", "AIN TEDELES"],
    "28": ["M'SILA", "BOU SAADA", "SIDI AISSA", "MAGRA"],
    "29": ["MASCARA", "SIG", "MOHAMMADIA", "GHRISS"],
    "30": ["OUARGLA", "HASSI MESSAOUD", "TOUGGOURT", "TEMACINE"],
    "31": ["ORAN", "ARZEW", "BIR EL DJIR", "ES SENIA", "AIN EL TURCK"],
    "32": ["EL BAYADH", "BOUGTOB", "EL ABIODH SIDI CHEIKH"],
    "33": ["ILLIZI", "DJANET", "IN AMENAS"],
    "34": ["BORDJ BOU ARRERIDJ", "RAS EL OUED", "MANSOURA"],
    "35": ["BOUMERDES", "DELLYS", "BORDJ MENAIEL", "THENIA", "KHEMIS EL KHECHNA"],
    "36": ["EL TARF", "EL KALA", "DREAN"],
    "37": ["TINDOUF"],
    "38": ["TISSEMSILT", "THENIET EL HAD", "LAAYOUNE"],
    "39": ["EL OUED", "GUEMAR", "MAGRANE"],
    "40": ["KHENCHELA", "KAIS", "CHECHAR"],
    # ... following wilayas (41-58) will show their chef-lieu + data from portfolio
}

def get_clean_hierarchy(portfolio_data):
    hierarchy = {}
    
    # Init with core data
    for code, name in OFFICIAL_WILAYAS.items():
        key = f"{code} - {name}"
        hierarchy[key] = set(CORE_COMMUNES.get(code, ["CHEF-LIEU"]))

    # Fill and merge with portfolio data
    for p in portfolio_data:
        w_raw = str(p.get('wilaya', '')).upper()
        c_raw = str(p.get('commune', '')).upper()
        
        # Match wilaya
        matched_key = None
        for code, name in OFFICIAL_WILAYAS.items():
            if name in w_raw:
                matched_key = f"{code} - {name}"
                break
        
        if matched_key and c_raw:
            hierarchy[matched_key].add(c_raw)

    # Convert to sorted lists
    return {k: sorted(list(v)) for k, v in sorted(hierarchy.items())}
