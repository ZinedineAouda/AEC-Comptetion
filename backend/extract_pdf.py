import pypdf
import os

pdf_path = r"C:\Users\zined\Documents\GitHub\AEC-Comptetion\Algerian_RPA99_Confined_Masonry.pdf"

def extract_text(path):
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

if os.path.exists(pdf_path):
    content = extract_text(pdf_path)
    # Save the first 5000 characters to a text file for inspection
    with open("pdf_extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Extraction complete. check pdf_extracted_text.txt")
else:
    print("PDF not found")
