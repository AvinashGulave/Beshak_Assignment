import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import json
import os
from docx import Document

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load spaCy model 
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = [
        {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r"[\w\.-]+@[\w\.-]+"}}]},
        {"label": "PHONE", "pattern": [{"TEXT": {"REGEX": r"\+?\d[\d\-\s]{7,}"}}]},
        {"label": "POLICY_NUMBER", "pattern": [{"TEXT": {"REGEX": r"[A-Z]{3}[0-9]{5}"}}]},
    ]
    ruler.add_patterns(patterns)

except Exception as e:
    print("spaCy model load failed:", e)
    nlp = None

def clean_line(line):
    line = re.sub(r'\b([A-Z]{1,5})\s+(\d{1,10})\b', r'\1\2', line)
    line = re.sub(r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'\1@\2', line)
    line = re.sub(r'(\+\d{1,3}-\d{3})\s*(\d+)', r'\1\2', line)
    line = re.sub(r'([₹$€])\s+([\d,]+)', r'\1\2', line)
    line = line.replace('■', '₹')
    line = re.sub(r'\s+', ' ', line)
    return line.strip()

def read_pdf(file_path):
    all_text = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            zoom = 300 / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, config='--psm 6')
            for line in text.split('\n'):
                clean = clean_line(line)
                if clean:
                    all_text.append(clean)
        return '\n'.join(all_text)
    except Exception as e:
        raise RuntimeError(f"PDF reading failed: {e}")

def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = [clean_line(line) for line in text.split('\n') if clean_line(line)]
        return '\n'.join(lines)
    except Exception as e:
        raise RuntimeError(f"TXT reading failed: {e}")

def read_docx(file_path):
    try:
        doc = Document(file_path)
        lines = [clean_line(p.text) for p in doc.paragraphs if clean_line(p.text)]
        return '\n'.join(lines)
    except Exception as e:
        raise RuntimeError(f"DOCX reading failed: {e}")

def read_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".txt":
        return read_txt(file_path)
    elif ext in [".docx", ".doc"]:
        return read_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_fields(text):
    try:
        name_match = re.search(r"Name:\s*(.+)", text)
        email_match = re.search(r"Email:\s*([\w\.-]+@[\w\.-]+)", text)
        phone_match = re.search(r"Phone:\s*(\+?\d[\d\s-]+)", text)
        policy_match = re.search(r"Policy\s*Number:\s*([A-Z0-9]+)", text)
        return {
            "name": name_match.group(1).strip() if name_match else None,
            "email": email_match.group(1).strip() if email_match else None,
            "phone": phone_match.group(1).strip() if phone_match else None,
            "policy_number": policy_match.group(1).strip() if policy_match else None
        }
    except Exception as e:
        raise RuntimeError(f"Field extraction failed: {e}")


def extract_with_ner(text):
    doc = nlp(text)
    extracted = {"name": None, "email": None, "phone": None, "policy_number": None}

    for ent in doc.ents:
        if ent.label_ == "PERSON" and not extracted["name"]:
            extracted["name"] = ent.text
        elif ent.label_ == "EMAIL":
            extracted["email"] = ent.text
        elif ent.label_ == "PHONE":
            extracted["phone"] = ent.text
        elif ent.label_ == "POLICY_NUMBER":
            extracted["policy_number"] = ent.text

    return extracted
if __name__ == "__main__":
    file_path = "sample_file.pdf"  
    if not os.path.exists(file_path):
        print("⚠️ File not found.")
    else:
        try:
            raw_text = read_document(file_path)
            if not raw_text.strip():
                print("⚠️ No readable text found in the document.")
            else:
                fields = extract_fields(raw_text)
                print("✅ Extracted Fields:")
                print(json.dumps(fields, indent=2))

                ner_fields = extract_with_ner(raw_text)
                if ner_fields:
                    print("\n🔍 Additional Fields (spaCy NER):")
                    print(json.dumps(ner_fields, indent=2))

        except Exception as e:
            print(f"Error processing document: {e}")
