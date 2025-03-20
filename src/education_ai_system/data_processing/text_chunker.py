# src/project_name/data_processing/text_chunker.py

def split_text_into_chunks(text, chunk_size=512, overlap=20):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks
