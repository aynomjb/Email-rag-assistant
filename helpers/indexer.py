from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os
import glob
import datetime

# 1. Setup: Embedding + Chroma
def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """
    Returns a HuggingFace embedding model instance.

    Args:
        model_name (str): Name of the HuggingFace sentence transformer model.

    Returns:
        HuggingFaceEmbeddings: An initialized embedding model.
    """
    return HuggingFaceEmbeddings(model_name=model_name)


def get_vectorstore(db_directory: str):
    """
    Initializes and returns a Chroma vectorstore with HuggingFace embeddings.
    
    Args:
        db_directory (str): Path to the ChromaDB persistence directory.
    
    Returns:
        Chroma: Configured vectorstore instance.
    """
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vectorstore = Chroma(
        persist_directory=db_directory,
        embedding_function=embedding_model
    )
    
    return vectorstore

# 2. Load and parse emails from .txt files

def parse_email_file2(filepath):
    with open(filepath, 'r') as f:
        raw = f.read()

    # Basic header extraction
    headers, body = raw.split("\n\n", 1)
    metadata = {}
    for line in headers.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip().lower()] = value.strip()

    return Document(
        page_content=body.strip(),
        metadata={
            "from": metadata.get("from"),
            "to": metadata.get("to"),
            "subject": metadata.get("subject"),
            "date": metadata.get("date"),
            "filename": filepath
        }
    )

def parse_email(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    headers, body = {}, []
    in_body = False
    for line in lines:
        if line.strip() == "":
            in_body = True
            continue
        if not in_body:
            key, val = line.split(":", 1)
            headers[key.strip().lower()] = val.strip()
        else:
            body.append(line)

    return Document(
        page_content="\n".join(body),
        metadata={
            "from": headers.get("from"),
            "to": headers.get("to"),
            "subject": headers.get("subject"),
            "date": headers.get("date"),
            "source": file_path
        }
    )


def parse_email_r(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    headers, body = {}, []
    in_body = False
    for line in lines:
        if line.strip() == "":
            in_body = True
            continue
        if not in_body:
            if ":" in line:
                key, val = line.split(":", 1)
                headers[key.strip().lower()] = val.strip()
        else:
            body.append(line)

    # Reverse trail logic: split by quote markers and reorder
    body_text = "\n".join(body)
    segments = body_text.split("\n---\n")
    reordered_body = "\n---\n".join(reversed(segments))  # latest reply first

    return Document(
        page_content=reordered_body.strip(),
        metadata={
            "from": headers.get("from"),
            "to": headers.get("to"),
            "subject": headers.get("subject"),
            "date": headers.get("date"),
            "source": os.path.basename(file_path)
        }
    )

# 3. Index all emails from a directory
def index_email_directory(email_dir="emails"):
    txt_files = glob.glob(os.path.join(email_dir, "*.txt"))
    txt_files = [f for f in txt_files if not f.endswith("-parsed.txt")]
    docs = [parse_email_r(fp) for fp in txt_files]
    vectorstore = get_vectorstore("chroma_email_db_3")
    vectorstore.add_documents(docs)
    vectorstore.persist()
    print(f"✅ Indexed {len(docs)} email(s) with trail into Chroma.")

# -----------------------------
# Run: Index and Query Example
# -----------------------------
# if __name__ == "__main__":
#     index_email_directory("emails")  # put your .txt emails in ./emails/

def delete_parsed_files(folder_path):
    """
    Deletes all files ending with '-parsed.txt' in the specified folder.

    Args:
        folder_path (str): Path to the folder containing parsed files.
    """
    parsed_files = glob.glob(os.path.join(folder_path, "*-parsed.txt"))
    
    for file_path in parsed_files:
        try:
            os.remove(file_path)
            print(f"🗑️ Deleted: {file_path}")
        except Exception as e:
            print(f"❌ Failed to delete {file_path}: {e}")
   
