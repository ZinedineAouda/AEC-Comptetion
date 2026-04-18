import re
import json

def parse_rpa_pdf():
    with open('docs/pdf_extracted_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by Wilaya names (looking for N° + Wilaya Name uppercase)
    # We'll use ANNEXE 1 section specifically
    annexe_text = text.split('ANNEXE 1')[1] if 'ANNEXE 1' in text else text
    
    # We'll look for Wilaya sections. They usually start with a number and name.
    # But since the text is messy, let's use a list of 48 wilayas to search.
    wilayas = [
        "ADRAR", "CHLEF", "LAGHOUAT", "OUM EL BOUAGHI", "BATNA", "BEJAIA", "BISKRA", 
        "BECHAR", "BLIDA", "BOUIRA", "TAMANRASSET", "TEBESSA", "TLEMCEN", "TIARET", 
        "TIZI-OUZOU", "ALGER", "DJELFA", "JIJEL", "SETIF", "SAIDA", "SKIKDA", 
        "SIDI BEL ABBES", "ANNABA", "GUELMA", "CONSTANTINE", "MEDEA", "MOSTAGANEM", 
        "M'SILA", "MASCARA", "OUARGLA", "ORAN", "EL BAYADH", "ILLIZI", "BORDJ BOU ARRERIDJ", 
        "BOUMERDES", "EL TARF", "TINDOUF", "TISSEMSILT", "EL OUED", "KHENCHELA", 
        "SOUK AHRAS", "TIPAZA", "MILA", "AIN DEFLA", "NAAMA", "AIN TEMOUCHENT", "GHARDAIA", "RELIZANE"
    ]

    registry = {}
    
    # Pre-filling with defaults from the PDF table 454-502
    # I'll just hardcode the defaults based on lines 506-552 for now
    defaults = {
        "ADRAR": "0", "CHLEF": "III", "LAGHOUAT": "I", "OUM EL BOUAGHI": "I", "BATNA": "I",
        "BEJAIA": "IIa", "BISKRA": "I", "BECHAR": "0", "BLIDA": "III", "BOUIRA": "IIa",
        "TAMANRASSET": "0", "TEBESSA": "I", "TLEMCEN": "I", "TIARET": "I", "TIZI-OUZOU": "IIa",
        "ALGER": "III", "DJELFA": "I", "JIJEL": "IIa", "SETIF": "IIa", "SAIDA": "I",
        "SKIKDA": "IIa", "SIDI BEL ABBES": "I", "ANNABA": "IIa", "GUELMA": "IIa",
        "CONSTANTINE": "IIa", "MEDEA": "IIa", "MOSTAGANEM": "IIa", "M'SILA": "I",
        "MASCARA": "IIa", "OUARGLA": "0", "ORAN": "IIa", "EL BAYADH": "I", "ILLIZI": "0",
        "BORDJ BOU ARRERIDJ": "IIa", "BOUMERDES": "III", "EL TARF": "IIa", "TINDOUF": "0",
        "TISSEMSILT": "IIa", "EL OUED": "0", "KHENCHELA": "I", "SOUK AHRAS": "I",
        "TIPAZA": "III", "MILA": "IIa", "AIN DEFLA": "IIa", "NAAMA": "I",
        "AIN TEMOUCHENT": "IIa", "GHARDAIA": "0", "RELIZANE": "III"
    }

    for w in wilayas:
        registry[w] = {"default": defaults.get(w, "I"), "groups": {}}

    # Extraction patterns
    # Groupe de communes [A/B/C] -> [Commune list] -> [Zone code]
    # This is a bit manual because the text is so fragmented.
    
    # CHLEF overrides
    registry["CHLEF"]["groups"] = {
        "IIb": ["EL KARIMIA", "HARCHOUN", "SENDJAS", "OUED SLY", "BOUKADIR"],
        "IIa": ["OULED BEN ABD EL KADER", "HADJADJ"]
    }
    
    # BLIDA overrides
    registry["BLIDA"]["groups"] = {
        "IIb": ["MEFTAH", "DJEBABRA", "SOUHANE", "LARBAA", "OULED ELAMA", "BOUGARA", "HAMMAM MELOUANE", "AIN ROMANA"]
    }

    # TIZI-OUZOU overrides
    registry["TIZI-OUZOU"]["groups"] = {
        "IIb": ["MIZRANA"]
    }

    # MEDEA overrides
    registry["MEDEA"]["groups"] = {
        "IIb": ["EL HAMDANIA", "MEDEA", "TAMESGUIDA"],
        "I": ["BOU AICHE", "CHAHBOUNIA", "BOUGHZOUL", "SAREG", "MEFTAHA", "OULED MAAREF", "EL AOUNET", "AIN BOUCIF", "SIDI DAMED", "AIN OUKSIR", "CHENIGUEL"]
    }

    # MOSTAGANEM overrides
    registry["MOSTAGANEM"]["groups"] = {
        "III": ["OULED BOUGHALEM", "ACHAACHA", "KHADRA", "NEKMARIA"],
        "IIb": ["SIDI LAKHDAR", "TASGHAIT", "OULED MAALAH"]
    }

    # M'SILA overrides
    registry["M'SILA"]["groups"] = {
        "IIa": ["BENI ILMANE", "OUNOUGHA", "HAMMAM DALA A", "TARMOUNT", "OULED MANSOUR", "M'SILA", "MTARFA", "MAADID", "OULED DERRADJ", "OULED ADDI", "DAHAHNA", "BERHOUM", "AIN KADRA", "MAGRA", "BELAIBA"]
    }

    # MASCARA overrides
    registry["MASCARA"]["groups"] = {
        "I": ["AIN FARES", "AIN FEKRAN", "BOUHANIFIA", "GUERDJOU", "OUED TARIA", "GHRIS", "BENAIN", "MOKHDA", "AOUF", "GHAROUS", "NESMOT", "M'HAMID", "HACHEM", "OUED EL ABTAL", "AIN FERRAH"]
    }

    # BOUMERDES overrides
    registry["BOUMERDES"]["groups"] = {
        "IIb": ["AFIR", "BENCHOUD", "TAOUERGA", "BAGHLIA", "OUED AISSA", "NACIRIA", "BORDJ MENAIL", "ISSER", "BENI AMRANE", "SOUK EL HAD", "BOUZEGZA KEDAR", "EL KHAROUBA", "LARBATACHE", "KHEMIS EL KHECHNA", "OULED MOUSSA", "HAMMADI"],
        "IIa": ["TIMEZRIT", "AMMAL", "CHAABET EL AMEUR"]
    }

    # AIN DEFLA overrides
    registry["AIN DEFLA"]["groups"] = {
        "III": ["TACHETA ZOUGAGHA", "EL ABADIA", "AIN BOUYAHIA", "EL ATTAF"],
        "IIb": ["EL AMRA", "MEKHTARIA", "ARIB", "ROUINA", "AIN DEFLA", "BOURASHED", "ZEDDINE", "TIBERKANINE", "SEN ALLAH", "MELIANA", "AIN TORKI", "HAMMAM RIGHA", "AIN BENIAN", "HOUCEINIA", "BOUMADFAA"]
    }

    # RELIZANE overrides
    registry["RELIZANE"]["groups"] = {
        "III": ["MEDIOUNA", "SIDI M'HAMED BEN ALI", "MAZOUNA", "EL GUETTAR"],
        "IIb": ["MERDJA SIDI ABED", "OUED RHIOU", "OUARTZENZ", "DJIDIOUIA", "HAMRI", "BENI ZENTIS"]
    }

    with open('data/seismic_registry_rpa.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4)

if __name__ == "__main__":
    parse_rpa_pdf()
