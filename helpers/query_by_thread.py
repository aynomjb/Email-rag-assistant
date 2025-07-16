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
    persist_directory="chroma_email_db_3",
    embedding_function=embedding_model
)


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


# 4. Query + Ask LLaMA 3.2 via Prompt Template
# ---------------------------------------------
def ask_email_agent(query, top_k=10):
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

    # print("\n🤖 Response from LLaMA 3.2:\n")
    # print(response)
    return response



def ask_email_agent2(query,email_dir, top_k=10):
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # More diverse retrieval
        search_kwargs={"k": top_k,
        "filter": {"thread": email_dir}
        }
    )
    docs = retriever.get_relevant_documents(query)

    if not docs:
        print("⚠️ No relevant documents found for the query.")
        return

    # Include metadata for better grounding
    context = "\n\n---\n\n".join([
        f"From: {doc.metadata.get('from', 'Unknown')}\n"
        f"To: {doc.metadata.get('to', 'Unknown')}\n"
        f"Subject: {doc.metadata.get('subject', 'No Subject')}\n"
        f"Date: {doc.metadata.get('date', 'Unknown')}\n\n"
        f"{doc.page_content.strip()}"
        for doc in docs
    ])

    # Stronger grounding prompt
    prompt = PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are an AI assistant helping analyze and summarize corporate email trails. Use only the information provided in the CONTEXT to answer the QUESTION. 
Be specific, and do not make assumptions beyond the content.

QUESTION:
{question}

CONTEXT:
{context}

📝 Answer:"""
    )

    llm = Ollama(model="llama3.2")  # Ensure Ollama is running locally

    final_prompt = prompt.format(question=query, context=context)
    response = llm.invoke(final_prompt)

    # print(response)
    return response


def ask_email_agent3(query,email_dir, top_k=10):
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # More diverse retrieval
        search_kwargs={"k": top_k,
        "filter": {"thread": email_dir}
        }
        
    )
    docs = retriever.get_relevant_documents(query)

    if not docs:
        print("⚠️ No relevant documents found for the query.")
        return

    # Include metadata for better grounding
    context = "\n\n---\n\n".join([
        f"From: {doc.metadata.get('from', 'Unknown')}\n"
        f"To: {doc.metadata.get('to', 'Unknown')}\n"
        f"Subject: {doc.metadata.get('subject', 'No Subject')}\n"
        f"Date: {doc.metadata.get('date', 'Unknown')}\n\n"
        f"{doc.page_content.strip()}"
        for doc in docs
    ])

    # Stronger grounding prompt
    prompt = PromptTemplate(
        input_variables=["question", "context"],
        template="""
You are an AI assistant helping analyze and summarize corporate email trails. Use only the information provided in the CONTEXT to answer the QUESTION. 
Be specific, and do not make assumptions beyond the content.

QUESTION:
{question}

CONTEXT:
{context}

📝 Answer:"""
    )

    llm = Ollama(model="llama3.2")  # Ensure Ollama is running locally

    final_prompt = prompt.format(question=query, context=context)
    response = llm.invoke(final_prompt)

    # print(response)
    return response, docs


# # -----------------------------
# # Run: Index and Query Example
# # -----------------------------
# if __name__ == "__main__":
#     # query_email_store("What did Alice mention on 2025-04-23?")
#     # ask_email_agent2("When is the kickoff meeting for Project Phoenix scheduled, and who is expected to attend?")
#     # ask_email_agent("Based on the email trail, who was explicitly included in the invite list for the Project Phoenix kickoff meeting?")
#     # ask_email_agent2("When is the Project Phoenix kickoff meeting scheduled?")
#     ask_email_agent2("What topics will be covered during the kickoff meeting?")


