# Document Field Extraction

This Python project extracts structured information such as **Name**, **Email**, **Phone Number**, and **Policy Number** from documents in various formats (PDF, DOCX, TXT). It uses a combination of **regular expressions** and **spaCy NER** for extraction, and can handle scanned PDFs using OCR.

---

## Features

- Reads and extracts text from:
  - PDF (including scanned PDFs with OCR)
  - DOCX
  - TXT
- Cleans and normalizes extracted text
- Extracts fields using:
  - Regex patterns for common fields
  - spaCy Named Entity Recognition (NER) with custom entity patterns
- Handles international phone numbers, currency symbols, and policy numbers dynamically
- Supports Tesseract OCR for image-based PDFs

---

## Dependencies

Install required libraries using `pip`:

```bash
pip install -r requirements.txt
pip install pdfplumber PyMuPDF pytesseract pillow python-docx spacy
python -m spacy download en_core_web_sm
```

You also need to install **Tesseract OCR**:

- Windows: [Tesseract Download](https://github.com/tesseract-ocr/tesseract)
- Linux: `sudo apt install tesseract-ocr`

Set the Tesseract path in the code:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## Usage

1. Place your document in the project folder (e.g., `sample_insurance_doc.pdf`).
2. Run the script:

```bash
python doc_info_extractor.py
```

3. The script will output:

- **Extracted Fields using Regex**:

```json
{
  "name": "Rahul Sharma",
  "email": "rahul.sharma@email.com",
  "phone": "+91-9876543210",
  "policy_number": "ABC12345"
}
```

- **Additional Fields using spaCy NER** (if available):

```json
{
  "name": "Rahul Sharma",
  "email": "rahul.sharma@email.com",
  "phone": "9876543210",
  "policy_number": "ABC12345"
}
```

---

## Functions Overview

- `read_document(file_path)` – Reads PDF, TXT, DOCX based on file extension
- `read_pdf(file_path)` – Extracts text from PDF using OCR if necessary
- `read_txt(file_path)` – Reads and cleans text from TXT files
- `read_docx(file_path)` – Reads and cleans text from DOCX files
- `clean_line(line)` – Cleans text lines, removes extra spaces, normalizes symbols
- `extract_fields(text)` – Extracts fields using regex patterns
- `extract_with_ner(text)` – Extracts fields using spaCy NER

---

## Notes

- Ensure that the spaCy model `en_core_web_sm` is installed.
- OCR accuracy depends on PDF quality; scanned documents may require high-resolution images.
- Regex-based extraction is dynamic but may need adjustment for custom formats.

---
