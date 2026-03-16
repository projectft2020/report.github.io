#!/usr/bin/env python3
import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        return None
    return text

if __name__ == "__main__":
    pdf_path = "/Users/charlie/.openclaw/workspace/kanban/works/browser-crawl-quantnews-ab739a31/robeco-efficient-factor-investing-strategies.pdf"
    output_path = "/Users/charlie/.openclaw/workspace/kanban/works/browser-crawl-quantnews-ab739a31/robeco-extracted.txt"

    text = extract_text_from_pdf(pdf_path)
    if text:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully extracted text to {output_path}")
        print(f"Total characters: {len(text)}")
    else:
        sys.exit(1)
