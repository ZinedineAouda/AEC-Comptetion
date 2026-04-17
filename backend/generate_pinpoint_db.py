import json

# This database is manually verified against the DTR B C 2-48 (RPA 99 / Version 2003) Annexe 1
# mapping communes to their specific seismic groups.

rpa_master_database = {
    "CHLEF": {
        "groups": {
            "IIb": ["EL KARIMIA", "HARCHOUN", "SENDJAS", "OUED SLY", "BOUKADIR"],
            "IIa": ["OULED BEN ABD EL KADER", "HADJADJ"]
        },
        "default": "III"
    },
    "BLIDA": {
        "groups": {
            "IIb": ["MEFTAH", "DJEBABRA", "SOUHANE", "LARBAA", "OULED EL SELAMA", "BOUGARA", "HAMMAM MELOUANE", "AIN ROMANA"]
        },
        "default": "III"
    },
    "TIZI-OUZOU": {
        "groups": {
            "IIb": ["MIZRANA"]
        },
        "default": "IIa"
    },
    "MEDEA": {
        "groups": {
            "IIb": ["EL HAMDANIA", "MEDEA", "TAMESGUIDA"],
            "I": ["BOU AICHE", "CHAHBOUNIA", "BOUGHZOUL", "SAREG", "MEFTAHA", "OULED MAREF", "EL AOUNET", "AIN BOUCIF", "SIDI DAMED", "AIN OUKSIR", "CHENIGUEL"]
        },
        "default": "IIa"
    },
    "MOSTAGANEM": {
        "groups": {
            "III": ["OULED BOUGHALEM", "ACHAACHA", "KHADRA", "NEKMARIA"],
            "IIb": ["SIDI LAKHDAR", "TASGHAIT", "OULED MAALAH"]
        },
        "default": "IIa"
    },
    "M'SILA": {
        "groups": {
            "IIa": ["BENI ILMANE", "OUNOUGHA", "HAMMAM DALA A", "TARMOUNT", "OULED MANSOUR", "M'SILA", "M'TARFA", "MAADID", "OULED DERRADJ", "OULED ADDI", "DAHAHNA", "BERHOUM", "AIN KADRA", "MAGRA", "BELAIBA"]
        },
        "default": "I"
    },
    "MASCARA": {
        "groups": {
            "I": ["AIN FARES", "AIN FEKRAN", "BOUHANIFIA", "GUERDJOU", "OUED TARIA", "GHRIS", "BENAIN", "MOKHDA", "AOUF", "GHAROUS", "NESMOT", "M'HAMID", "HACHEM", "OUED EL ABTAL", "AIN FERRAH"]
        },
        "default": "IIa"
    },
    "BOUMERDES": {
        "groups": {
            "IIb": ["AFIR", "BENCHOUD", "TAOUERGA", "BAGHLIA", "OUED AISSA", "NACIRIA", "BORDJ MENAIL", "ISSER", "BENI AMRANE", "SOUK EL HAD", "BOUZEGZA KEDAR", "EL KHAROUBA", "LARBATACHE", "KHEMIS EL KHECHNA", "OULED MOUSSA", "HAMMADI"],
            "IIa": ["TIMEZRIT", "AMMAL", "CHAABET EL AMEUR"]
        },
        "default": "III"
    },
    "AIN DEFLA": {
        "groups": {
            "III": ["TACHETA", "ZOUGAGHA", "EL ABADIA", "AIN BOUYAHIA", "EL ATTAF"],
            "IIb": ["EL AMRA", "MEKHTARIA", "ARIB", "ROUINA", "AIN DEFLA", "BOURASHED", "ZEDDINE", "TIBERKANINE", "SEN ALLAH", "MELIANA", "AIN TORKI", "HAMMAM RIGHA", "AIN BENIAN", "HOUCEINIA", "BOUMADFAA"]
        },
        "default": "IIa"
    },
    "RELIZANE": {
        "groups": {
            "III": ["MEDIOUNA", "SIDI M'HAMED BEN ALI", "MAZOUNA", "EL GUETTAR"],
            "IIb": ["MERDJA SIDI ABED", "OUED RHIOU", "OUARTZENZ", "DJIDIOUIA", "HAMRI", "BENI ZENTIS"]
        },
        "default": "IIa"
    },
    # Generic Wilaya defaults
    "ADRAR": {"default": "0"},
    "LAGHOUAT": {"default": "I"},
    "OUM EL BOUAGHI": {"default": "I"},
    "BATNA": {"default": "I"},
    "BEJAIA": {"default": "IIa"},
    "BISKRA": {"default": "I"},
    "BECHAR": {"default": "0"},
    "BOUIRA": {"default": "IIa"},
    "TAMENRASSET": {"default": "0"},
    "TEBESSA": {"default": "I"},
    "TLEMCEN": {"default": "I"},
    "TIARET": {"default": "I"},
    "ALGER": {"default": "III"},
    "DJELFA": {"default": "I"},
    "JIJEL": {"default": "IIa"},
    "SETIF": {"default": "IIa"},
    "SAIDA": {"default": "I"},
    "SKIKDA": {"default": "IIa"},
    "SIDI BEL - ABBES": {"default": "I"},
    "ANNABA": {"default": "IIa"},
    "GUELMA": {"default": "IIa"},
    "CONSTANTINE": {"default": "IIa"},
    "OUARGLA": {"default": "0"},
    "ORAN": {"default": "IIa"},
    "EL BAYADH": {"default": "I"},
    "ILLIZI": {"default": "0"},
    "BORDJ BOU ARRERIDJ": {"default": "IIa"},
    "EL TARF": {"default": "IIa"},
    "TINDOUF": {"default": "0"},
    "TISSEMSILT": {"default": "IIa"},
    "EL OUED": {"default": "0"},
    "KHENCHELA": {"default": "I"},
    "SOUK AHRAS": {"default": "I"},
    "TIPAZA": {"default": "III"},
    "MILA": {"default": "IIa"},
    "NAAMA": {"default": "I"},
    "AIN TEMOUCHENT": {"default": "IIa"},
    "GHARDAIA": {"default": "0"},
    "EL M'GHAIR": {"default": "0"},
    "EL MENIAA": {"default": "0"},
    "OULED DJELLAL": {"default": "I"},
    "BORDJ B. MOKHTAR": {"default": "0"},
    "BENI ABBES": {"default": "0"},
    "TIMIMOUN": {"default": "0"},
    "TOUGGOURT": {"default": "0"},
    "DJANET": {"default": "0"},
    "IN SALAH": {"default": "0"},
    "IN GUEZZAM": {"default": "0"}
}

with open('web_dashboard/public/communes_rpa.json', 'w', encoding='utf-8') as f:
    json.dump(rpa_master_database, f, indent=4)
