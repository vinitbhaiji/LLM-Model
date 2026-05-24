import os
from pypdf import PdfReader
from docx import Document

from app.core.logger import logger

DATA_DIR = "data"


def ensure_data_directory():

    if not os.path.exists(DATA_DIR):

        os.makedirs(DATA_DIR)


def save_file(file):

    ensure_data_directory()

    file_path = os.path.join(
        DATA_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        buffer.write(
            file.file.read()
        )

    logger.info(
        f"File saved: {file.filename}"
    )

    return file_path


def read_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        text += page.extract_text()

    return text


def read_docx(file_path):

    doc = Document(file_path)

    text = ""

    for para in doc.paragraphs:

        text += para.text

    return text


def extract_text(file_path):

    if file_path.endswith(".txt"):

        return read_txt(file_path)

    elif file_path.endswith(".pdf"):

        return read_pdf(file_path)

    elif file_path.endswith(".docx"):

        return read_docx(file_path)

    else:

        raise ValueError(
            "Unsupported file type"
        )
    
def chunk_text(text, chunk_size=300, overlap=30):

    chunks = []

    start = 0

    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks