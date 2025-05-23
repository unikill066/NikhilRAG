#!/usr/bin/env python3

# imports
from bs4 import BeautifulSoup
import os, sys, shutil, openai
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader, BSHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import constants


load_dotenv()
DATA_PATH, CHROMA_PATH = constants.DATA_PATH, constants.CHROMA_DB_PATH


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    documents = list()
    loaders = {
        ".md": DirectoryLoader(DATA_PATH, glob="*.md"),
        ".pdf": DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader),
        ".docx": DirectoryLoader(DATA_PATH, glob="*.docx", loader_cls=Docx2txtLoader),
        ".html": DirectoryLoader(DATA_PATH, glob="*.html", loader_cls=BSHTMLLoader)
    }

    for ext, loader in loaders.items():
        try:
            docs = loader.load()
            print(f"Loaded {len(docs)} {ext} documents")
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {ext} documents: {e}")
    
    print(f"Loaded {len(documents)} total documents from {DATA_PATH}")
    return documents



def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    chroma_dir = str(CHROMA_PATH) if not isinstance(CHROMA_PATH, str) else CHROMA_PATH
    if os.path.exists(chroma_dir):
        if constants.RECREATE_EMBEDDINGS:
            print("Decommissioning the vector-db to recreate a new set of embeddings.")
            shutil.rmtree(chroma_dir)
            db = Chroma.from_documents(
                chunks, OpenAIEmbeddings(model=constants.MODEL), persist_directory=chroma_dir)
            db.persist()
            print("New chromadb recreated!")
            print(f"Saved {len(chunks)} chunks to {chroma_dir}.")
        else:
            print("Vector store already exists and RECREATE_EMBEDDINGS is False. Using existing database.")
    else:
        db = Chroma.from_documents(
            chunks, OpenAIEmbeddings(model=constants.MODEL), persist_directory=chroma_dir)
        db.persist()
        print("New chromadb created!")
        print(f"Saved {len(chunks)} chunks to {chroma_dir}.")

if __name__ == "__main__":
    main()