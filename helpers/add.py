from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os
import glob
import datetime

# 1. Setup: Embedding + Chroma
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="chroma_email_db",
    embedding_function=embedding_model
)

# 2. Load and parse emails from .txt files
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
    docs = [parse_email_r(fp) for fp in txt_files]
    vectorstore.add_documents(docs)
    vectorstore.persist()
    print(f"✅ Indexed {len(docs)} email(s) with trail into Chroma.")

# 4. Query the email vectorstore
def query_email_store(question):
    retriever = vectorstore.as_retriever()
    results = retriever.get_relevant_documents(question)
    print("\n🔎 Top Matches:\n")
    for doc in results:
        print("---")
        print(f"Subject: {doc.metadata.get('subject')}")
        print(f"From: {doc.metadata.get('from')}")
        print(doc.page_content[:300], "...")

def add_single_email_to_index(file_path):
    new_doc = parse_email(file_path)
    vectorstore.add_documents([new_doc])
    vectorstore.persist()
    print(f"✅ Added '{os.path.basename(file_path)}' to Chroma DB.")

# 4. Query + Ask LLaMA 3.2 via Prompt Template
# ---------------------------------------------
def ask_email_agent(query, top_k=4):
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query, k=top_k)

    context = "\n\n---\n\n".join([doc.page_content for doc in docs])

    prompt = PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are an assistant helping analyze and summarize email trails.

Based on the CONTEXT below, answer the QUESTION in a helpful, clear way.

QUESTION:
{question}

CONTEXT:
{context}

📝 Answer:"""
    )

    llm = Ollama(model="llama3.2")  # Make sure ollama is running

    final_prompt = prompt.format(question=query, context=context)
    response = llm.invoke(final_prompt)

    print("\n🤖 Response from LLaMA 3.2:\n")
    print(response)

# -----------------------------
# Run: Index and Query Example
# -----------------------------
if __name__ == "__main__":
    new_file = "emails/new_email.txt"
    add_single_email_to_index(new_file)

    # Optionally test it
    ask_email_agent("What did Alice mention on 2025-04-23?")
    # index_email_directory("emails")  # put your .txt emails in ./emails/
    # query_email_store("What did Alice say about project progress?")
    # ask_email_agent("What did Alice say about project progress?")
