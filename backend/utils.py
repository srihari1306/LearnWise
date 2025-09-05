import os
from werkzeug.utils import secure_filename
from pypdf import PdfReader

def save_upload(file_obj, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    filename = secure_filename(file_obj.filename)
    path = os.path.join(dest_folder, filename)
    file_obj.save(path)
    return filename, path

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)

def chunk_text(text, max_tokens=200):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunk_text_content = " ".join(words[start:end])
        chunks.append((start, end, chunk_text_content))
        start = end
    return chunks
