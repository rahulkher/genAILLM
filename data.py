
import streamlit as st  # Import the Streamlit library for building the web application
from langchain_chroma import Chroma  # Import Chroma from Langchain for database functionality
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # Import tokenizer and model for sequence-to-sequence tasks
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader, DirectoryLoader, TextLoader  # Import loaders for different document types
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Import text splitter to divide text into chunks
from langchain_community.embeddings import SentenceTransformerEmbeddings  # Import embeddings from SentenceTransformer
from langchain_community.embeddings.ollama import OllamaEmbeddings  # Import Ollama embeddings
from langchain.chains import RetrievalQA  # Import RetrievalQA for question answering
import os  # Import os for operating system functionalities
from pathlib import Path



# # Define paths for data storage
BASE_PATH = Path(__file__).parent
# Define the path where the documents will be stored
DATA_PATH = os.path.join(BASE_PATH, 'docs')
CHROMA_DIR = os.path.join(BASE_PATH, 'db')

# Define the directory for storing the vector database
persist_directory = 'db'

def pdf_loader(path: str):
    """
    Load PDF documents from the specified directory.
    :param path: Path to the directory containing PDF files.
    :return: List of loaded documents.
    """
    print("Reading PDFs in the directory")
    pdf_loader = PyPDFDirectoryLoader(path=path)
    documents = pdf_loader.load()
    return documents

def pdf_loader1(path:str, file:str):
    pdf_loader = PyPDFLoader(os.path.join(path, file))
    documents = pdf_loader.load()
    return documents

def split_documents(chunk_size: int, chunk_overlap: int, path: str, file:str=''):
    """
    Split documents into smaller chunks.
    :param chunk_size: Size of each chunk.
    :param chunk_overlap: Overlap between chunks.
    :param path: Path to the directory containing PDF files.
    :return: List of text chunks.
    """
    print("Splitting the PDFs")
    # Splitting the text in chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(pdf_loader1(path, file))
    return texts




def get_embedding_function():
    """
    Initialize and return the embedding function.
    This function transforms text into numerical vectors that the AI model can understand.
    :return: Embedding function.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

def make_text_ids(texts):
    """
    Assign unique IDs to each text chunk.
    :param texts: List of text chunks.
    """
    print("Marking chunks")
    last_page_id = None
    current_chunk_index = 0

    for text in texts:
        source = text.metadata.get("source")
        page = text.metadata.get("page")
        current_page_id = f"{source}:{page}"
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
            last_page_id = current_page_id

        text_id = f"{source}:{page}:{current_chunk_index}"
        text.metadata["id"] = text_id

def add_to_db(texts):
    """
    Add text chunks to the Chroma database.
    :param texts: List of text chunks.
    """
    make_text_ids(texts=texts)
    print("Loading vector database")
    db = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embedding_function()
    )

    # Get existing documents in the database
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in Database: {len(existing_ids)}")

    # Filter out texts that are already in the database
    new_texts = []
    for text in texts:
        if text.metadata["id"] not in existing_ids:
            new_texts.append(text)
    print(f"{len(new_texts)} documents found to be added...")

    # Add new texts to the database
    new_text_ids = [text.metadata["id"] for text in new_texts]
    try:
        db.add_documents(new_texts, ids=new_text_ids)
        print(f"{len(new_texts)} documents added")
    except ValueError:
        print("No new documents being added...")
   

    return new_texts, existing_ids

def delete_from_db(filenames:list):
    if len(filenames) >0:

        db = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=get_embedding_function()
        )
        
        metadatas = db.get()['metadatas']
        sources = [metadata.get('source').split('/')[-1] for metadata in metadatas]
        ids = db.get()['ids']
        file_to_id_map = {}

        for source in sources:
            idlilst = []
            for id in ids:
                checkid  = id.split(":")[1].split('/')[-1]
                if source == checkid:
                    idlilst.append(id)
            file_to_id_map[source] = idlilst
        
        ids_to_delete = []
        for file in filenames:
            ids_to_delete.extend(file_to_id_map[file])
        
        if len(ids_to_delete) > 100:
            for i in range(0, len(ids_to_delete), 100):
                db.delete(ids_to_delete[i:i+100])
            return True, {'message':f"{filenames} deleted from database"}
        else:
            db.delete(ids_to_delete)
            return True, {'message':filenames}
    else:
        return False, {'error': 'No files to delete'}

if __name__=="__main__":
    # Split the documents into chunks
    texts = split_documents(chunk_size=1000, chunk_overlap=200, path=DATA_PATH)
    # Add the text chunks to the database
    add_to_db(texts=texts)
