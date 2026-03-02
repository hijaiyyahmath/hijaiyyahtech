import json
import hashlib
import unicodedata

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

HIJAIYYAH_SET = "ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي".split()

def generate():
    # Load Fa and Waw
    with open("CSGI_fa.json", "r", encoding="utf-8") as f:
        fa_data = json.load(f)
    with open("CSGI_waw.json", "r", encoding="utf-8") as f:
        waw_data = json.load(f)
    with open("CSGI_jim.json", "r", encoding="utf-8") as f:
        jim_data = json.load(f)

    # Use Fa as template for dummies (but clear some stuff)
    template = fa_data.copy()
    
    letters_list = []
    for char in HIJAIYYAH_SET:
        if char == "ف":
            letters_list.append(fa_data)
        elif char == "و":
            letters_list.append(waw_data)
        elif char == "ج":
            letters_list.append(jim_data)
        elif char == "ه":
            # Dataset stores "هـ" but id maps to "ه"
            heh_tatweel = template.copy()
            heh_tatweel["letter"] = "هـ"
            heh_tatweel["meta"] = template["meta"].copy()
            heh_tatweel["notes"] = "Dummy entry for هـ"
            letters_list.append(heh_tatweel)
        else:
            dummy = template.copy()
            dummy["letter"] = char
            dummy["meta"] = template["meta"].copy()
            dummy["meta"]["notes"] = f"Dummy entry for {char}"
            letters_list.append(dummy)
    
    root = {
        "csgi_version": "CSGI-DATASET-1.0",
        "csgi_dataset_version": "CSGI-DATASET-1.0",
        "letters": letters_list
    }
    
    with open("CSGI-28-v1.0.json", "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)

    # Calculate SHA256
    sha = hashlib.sha256(open("CSGI-28-v1.0.json", "rb").read()).hexdigest()
    print(f"SHA256: {sha}")

if __name__ == "__main__":
    generate()
