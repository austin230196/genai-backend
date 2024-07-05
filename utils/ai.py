import os
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter


CHROMA_PATH="../data/chroma"


def load_documents(doc: str):
    """
        We use this function to load our document
        @param {str} doc: the document name

        @return {str}: the documents 
    """
    #first we check the type of the doc
    allowed_types = {
        "pdf": PyPDFLoader,
        "txt": TextLoader,
        "md": TextLoader
    }
    doc_type = get_doctype(doc)
    if doc_type not in allowed_types:
        raise KeyError(f"{doc_type} is not allowed")
    
    path = f"{Path(__file__).parent}/../data/books/{doc}"
    loader = allowed_types[doc_type](path)
    documents = loader.load()
    return documents

def split_text(docs):
    """
        This function takes in a document and splits it into chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents=docs)
    print(f"Split documents into {len(chunks)} chunks.")
    # print(document.page_content)
    # print(document.metadata)
    return chunks


def get_retriever():
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=gemini_embeddings
    )
    retriever = vector_store.as_retriever()
    return retriever



def save_to_chroma(chunks):
    """
        This function takes in the chunks and then saves it to our Chroma vector database
    """
    #clear out database first
    # if os.path.exists(CHROMA_PATH):
    #     shutil.rmtree(CHROMA_PATH)
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = Chroma.from_documents(
        chunks,
        gemini_embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}")


def get_doctype(doc: str) -> str:
    """
        Get the type of the document type
        @param {str} doc: the document name

        @return {str}: the type 
    """
    doc_type = doc.split(".")[-1]
    return doc_type

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def generate_rag_chain():
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, top_p=0.85)

    # Prompt template to query Gemini
    llm_prompt_template = """You are an assistant for question-answering tasks.
    Use the following context to answer the question.
    If you don't know the answer, just say that you don't know.
    Use five sentences maximum and keep the answer concise.\n
    Question: {question} \nContext: {context} \nAnswer:"""
    llm_prompt = PromptTemplate.from_template(llm_prompt_template)
    rag_chain = (
        {"context": get_retriever() | format_docs, "question": RunnablePassthrough()}
        | llm_prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain