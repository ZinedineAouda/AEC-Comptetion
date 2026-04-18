import json

# This database is manually verified against the DTR B C 2-48 (RPA 99 / Version 2003) Annexe 1
# mapping communes to their specific seismic groups.

rpa_master_database = {
    "CHLEF": {
        "groups": {
            "IIb": [
                "EL KARIMIA",
                "HARCHOUN",
                "SENDJAS",
                "OUED SLY",
                "BOUKADIR"
            ],
            "IIa": [
                "OULED BEN.AEK",
                "EL HADJADJ"
            ]
        },
        "default": "III"
    },
    "BLIDA": {
        "groups": {
            "IIb": [
                "MEFTAH",
                "DJEBABRA",
                "SOUHANE",
                "LARBAA",
                "OULED SLAMA",
                "BOUGARA",
                "HAMMAM MELOUANE",
                "AIN ROMANA"
            ]
        },
        "default": "III"
    },
    "TIZI-OUZOU": {
        "groups": {
            "IIb": [
                "MIZRANA"
            ]
        },
        "default": "IIa"
    },
    "MEDEA": {
        "groups": {
            "IIb": [
                "EL HAMDANIA",
                "MEDEA",
                "TAMESGUIDA"
            ],
            "I": [
                "BOU AICHE",
                "CHAHBOUNIA",
                "BOUGHEZOUL",
                "SANEG",
                "MEFTAHA",
                "OULED MAAREF",
                "EL OUINET",
                "AIN BOUCIF",
                "SIDI DAMED",
                "AIN OUKSIR",
                "CHENIGUEL"
            ]
        },
        "default": "IIa"
    },
    "MOSTAGANEM": {
        "groups": {
            "III": [
                "OULED BOUGHALEM",
                "ACHAACHA",
                "KHADRA",
                "NEKMARIA"
            ],
            "IIb": [
                "SIDI LAKHDAR",
                "TAZGAIT",
                "OULED MAALEF"
            ]
        },
        "default": "IIa"
    },
    "M'SILA": {
        "groups": {
            "IIa": [
                "BENI ILMANE",
                "OUANOUGHA",
                "HAMMAM DHALAA",
                "TARMOUNT",
                "OULED MANSOUR",
                "M'SILA",
                "MTARFA",
                "MAADID",
                "OULED DERRADJ",
                "OULED ADDI GUEBALA",
                "DEHAHNA",
                "BERHOUM",
                "AIN KHADRA",
                "MAGRA",
                "BELAIBA"
            ]
        },
        "default": "I"
    },
    "MASCARA": {
        "groups": {
            "I": [
                "AIN FARES",
                "AIN FEKAN",
                "BOU HANIFIA",
                "GUERDJOUM",
                "OUED TARIA",
                "GHRISS",
                "BENIAN",
                "MAKDHA",
                "AOUF",
                "GHARROUS",
                "NESMOT",
                "MOHAMMADIA",
                "EL HACHEM",
                "OUED EL ABTAL",
                "AIN FERAH"
            ]
        },
        "default": "IIa"
    },
    "BOUMERDES": {
        "groups": {
            "IIb": [
                "AFIR",
                "BENCHOUD",
                "TAOURGA",
                "BAGHLIA",
                "OULED AISSA",
                "NACIRIA",
                "BORDJ MENAIEL",
                "ISSER",
                "BENI AMRANE",
                "SOUK EL HAD",
                "BOUZEGZA KEDARA",
                "EL KHARROUBA",
                "LARBATACHE",
                "KHEMIS EL KHECHNA",
                "OULED MOUSSA",
                "HAMMEDI"
            ],
            "IIa": [
                "TIMEZRIT",
                "AMMAL",
                "CHAABET EL AMEUR"
            ]
        },
        "default": "III"
    },
    "AIN DEFLA": {
        "groups": {
            "III": [
                "TACHETA ZEGAGHA",
                "EL ABADIA",
                "AIN BOUYAHIA",
                "EL ATTAF"
            ],
            "IIb": [
                "EL AMRA",
                "MEKHATRIA",
                "ARIB",
                "ROUINA",
                "AIN DEFLA",
                "BOURACHED",
                "ZEDDINE",
                "TIBERKANINE",
                "BEN ALLEL",
                "MILIANA",
                "AIN TORKI",
                "HAMMAM RIGHA",
                "AIN BENIAN",
                "HOCEINIA",
                "BOU MEDFAA"
            ]
        },
        "default": "IIa"
    },
    "RELIZANE": {
        "groups": {
            "III": [
                "MEDIOUNA",
                "SIDI M'HAMED BEN ALI",
                "MAZOUNA",
                "EL GUETTAR"
            ],
            "IIb": [
                "MERDJA SIDI ABED",
                "OUED RHIOU",
                "OUARIZANE",
                "DJIDIOUIA",
                "EL HAMRI",
                "BENI ZENTIS"
            ]
        },
        "default": "IIa"
    },
    "ADRAR": {
        "default": "0"
    },
    "LAGHOUAT": {
        "default": "I"
    },
    "OUM EL BOUAGHI": {
        "default": "I"
    },
    "BATNA": {
        "default": "I"
    },
    "BEJAIA": {
        "default": "IIa"
    },
    "BISKRA": {
        "default": "I"
    },
    "BECHAR": {
        "default": "0"
    },
    "BOUIRA": {
        "default": "IIa"
    },
    "TAMANRASSET": {
        "default": "0"
    },
    "TEBESSA": {
        "default": "I"
    },
    "TLEMCEN": {
        "default": "I"
    },
    "TIARET": {
        "default": "I"
    },
    "ALGER": {
        "default": "III"
    },
    "DJELFA": {
        "default": "I"
    },
    "JIJEL": {
        "default": "IIa"
    },
    "SETIF": {
        "default": "IIa"
    },
    "SAIDA": {
        "default": "I"
    },
    "SKIKDA": {
        "default": "IIa"
    },
    "SIDI BEL ABBES": {
        "default": "I"
    },
    "ANNABA": {
        "default": "IIa"
    },
    "GUELMA": {
        "default": "IIa"
    },
    "CONSTANTINE": {
        "default": "IIa"
    },
    "OUARGLA": {
        "default": "0"
    },
    "ORAN": {
        "default": "IIa"
    },
    "EL BAYADH": {
        "default": "I"
    },
    "ILLIZI": {
        "default": "0"
    },
    "BORDJ BOU ARRERIDJ": {
        "default": "IIa"
    },
    "EL TARF": {
        "default": "IIa"
    },
    "TINDOUF": {
        "default": "0"
    },
    "TISSEMSILT": {
        "default": "IIa"
    },
    "EL OUED": {
        "default": "0"
    },
    "KHENCHELA": {
        "default": "I"
    },
    "SOUK AHRAS": {
        "default": "I"
    },
    "TIPAZA": {
        "default": "III"
    },
    "MILA": {
        "default": "IIa"
    },
    "NAAMA": {
        "default": "I"
    },
    "AIN TEMOUCHENT": {
        "default": "IIa"
    },
    "GHARDAIA": {
        "default": "0"
    },
    "EL M'GHAIER": {
        "default": "0"
    },
    "EL MENIAA": {
        "default": "0"
    },
    "OULED DJELLAL": {
        "default": "I"
    },
    "BORDJ BADJI MOKHTAR": {
        "default": "0"
    },
    "BENI ABBES": {
        "default": "0"
    },
    "TIMIMOUN": {
        "default": "0"
    },
    "TOUGGOURT": {
        "default": "0"
    },
    "DJANET": {
        "default": "0"
    },
    "IN SALAH": {
        "default": "0"
    },
    "IN GUEZZAM": {
        "default": "0"
    }
}

# Save to both locations
paths = ['web_dashboard/public/communes_rpa.json', 'data/seismic_registry_rpa.json']
for p in paths:
    try:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(rpa_master_database, f, indent=4)
    except:
        pass

