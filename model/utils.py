from pypdf import PdfReader
import os

def load_pdfs_from_folder(folder_path):
    texts = []
    metadata = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(folder_path, file))

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    texts.append(text)
                    metadata.append({
                        "source": file,
                        "page": page_num
                    })

    return texts, metadata


def chunk_text(texts, chunk_size=500, overlap=200):
    chunks = []
    chunk_metadata = []

    for i, text in enumerate(texts):
        for j in range(0, len(text), chunk_size - overlap):
            chunk = text[j:j + chunk_size]
            chunks.append(chunk)
            chunk_metadata.append(texts[i])

    return chunks, chunk_metadata