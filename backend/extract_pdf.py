import pypdf
import os

# Robust path detection
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(base_dir, "docs", "Algerian_RPA99_Confined_Masonry.pdf")

def extract_text(path):
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

if os.path.exists(pdf_path):
    content = extract_text(pdf_path)
    output_path = os.path.join(base_dir, "docs", "pdf_extracted_text.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Extraction complete. check {output_path}")
else:
    # Try fallback to root if not in docs
    alt_pdf_path = os.path.join(base_dir, "Algerian_RPA99_Confined_Masonry.pdf")
    if os.path.exists(alt_pdf_path):
        content = extract_text(alt_pdf_path)
        output_path = os.path.join(base_dir, "docs", "pdf_extracted_text.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Extraction complete (from root). check {output_path}")
    else:
        print(f"PDF not found at {pdf_path}")
