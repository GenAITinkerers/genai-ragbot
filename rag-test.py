# for UI Framework
import streamlit as st
# for handling file operations and delays
import os
import shutil
import time # Import time for a small delay
# for embedding model and vector store
from langchain_community.vectorstores import Chroma
# for loading documents from directories
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
# for splitting text into manageable chunks Next session
from langchain.text_splitter import RecursiveCharacterTextSplitter
# for embedding model
from langchain_community.embeddings import SentenceTransformerEmbeddings

# --- Configuration ---
DATA_DIRECTORY = "./data_source" # Directory where your local TXT/PDF files are stored
PERSIST_DIRECTORY = "./today"  # Directory to store Chroma DB data persistently
COLLECTION_NAME = "testing1"

def ingest_documents():
    """
    Ingests documents from DATA_DIRECTORY, processes them, and stores them in Chroma DB.
    """
    print("Starting document ingestion process...")
    st.info("Initializing embedding model...")

    # Initialize Embedding Model
    try:
        embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
        print("SentenceTransformer Embeddings initialized successfully.")
    except Exception as e:
        print(f"Error initializing SentenceTransformer Embeddings: {e}")
        st.error(f"Error initializing embedding model: {e}")
        return False

    # Load documents from DATA_DIRECTORY
    st.info(f"Loading documents from: {DATA_DIRECTORY}")
    documents = []
    try:
        # Load PDF files
        pdf_loader = DirectoryLoader(
            DATA_DIRECTORY,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            silent_errors=True
        )
        pdf_documents = pdf_loader.load()
        documents.extend(pdf_documents)

        # Load TXT files
        txt_loader = DirectoryLoader(
            DATA_DIRECTORY,
            glob="**/*.txt",
            loader_cls=TextLoader,
            silent_errors=True
        )
        txt_documents = txt_loader.load()
        documents.extend(txt_documents)

        print(f"Loaded {len(documents)} documents (PDFs and TXTs).")
        st.success(f"Loaded {len(documents)} documents.")

        if not documents:
            print(f"No documents found in {DATA_DIRECTORY}. Please place your files there.")
            st.warning(f"No documents found in {DATA_DIRECTORY}. Please place your files there.")
            return False

    except Exception as e:
        print(f"Error loading documents: {e}")
        st.error(f"Error loading documents: {e}")
        return False

    # Split documents into chunks
    st.info("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_documents = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunked_documents)} chunks.")
    st.success(f"Split documents into {len(chunked_documents)} chunks.")

    # Clean existing Chroma DB for a fresh index
    st.info(f"Clearing existing Chroma DB at: {PERSIST_DIRECTORY}...")
    if os.path.exists(PERSIST_DIRECTORY):
        try:
            shutil.rmtree(PERSIST_DIRECTORY)
            print(f"Successfully cleared existing Chroma DB at: {PERSIST_DIRECTORY}")
            time.sleep(0.5) # Small delay to ensure directory is released
        except OSError as e:
            print(f"Error removing existing Chroma DB directory {PERSIST_DIRECTORY}: {e}")
            st.error(f"Error clearing old database: {e}. Please manually delete the '{PERSIST_DIRECTORY}' folder if the issue persists.")
            return False
    
    # Ensure directory exists, creating if necessary
    try:
        os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
        print(f"Ensured {PERSIST_DIRECTORY} directory exists.")
    except OSError as e:
        print(f"Error creating directory {PERSIST_DIRECTORY}: {e}")
        st.error(f"Error creating database directory: {e}. Check permissions.")
        return False

    # Store in Chroma DB
    st.info(f"Generating embeddings and storing in Chroma DB at {PERSIST_DIRECTORY}...")
    try:
        vectorstore = Chroma.from_documents(
            documents=chunked_documents, # Use chunked documents
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
            collection_name=COLLECTION_NAME
        )
        vectorstore.persist() # Ensure data is saved to disk
        print("Chroma DB built and persisted successfully!")
        st.success("Chroma DB built and persisted successfully!")
        return True
    except Exception as e:
        print(f"Error building and persisting Chroma DB: {e}")
        st.error(f"Error building and persisting Chroma DB: {e}. Check your files and permissions.")
        return False


def retrieve_and_generate_with_rag(query, vectorstore, k=3):
    """
    Retrieves relevant documents from the vector store and generates a response.
    """
    try:
        # Retrieve relevant documents
        retrieved_docs = vectorstore.similarity_search(query, k=k)
        
        if not retrieved_docs:
            return None, "I couldn't find relevant information for your query. Please try rephrasing or ask about topics covered in the ingested documents."
        
        # Combine retrieved documents
        combined_docs = "\n\n".join([f"--- Document Source: {doc.metadata.get('source', 'Unknown')} ---\n{doc.page_content}" for doc in retrieved_docs])
        
        # For this mock version, we'll create a simple response based on retrieved content
        # In a real RAG system, this would be passed to an LLM for generation
        generated_answer = f"Based on the retrieved documents, here's what I found:\n\n{combined_docs[:1000]}..." # Show a bit more content
        if len(combined_docs) > 1000: # Adjust truncation length
            generated_answer += "\n\n[Content truncated for display]"
        
        return combined_docs, generated_answer
        
    except Exception as e:
        return None, f"Error during retrieval: {str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="RAG App with Vector Store", layout="centered")

st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stExpander {
        border-radius: 10px;
        border: 1px solid #ddd;
        background-color: #ffffff;
        margin-top: 15px;
    }
    .stExpander>div>div>p {
        font-family: 'Inter', sans-serif;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    h2 {
        color: #34495e;
        font-family: 'Inter', sans-serif;
    }
    p {
        font-family: 'Inter', sans-serif;
        color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("RAG App with Vector Store")
st.write("This application uses your ingested documents from the vector store to answer questions. Make sure you have run the document ingestion process first.")

# --- Vector Store Initialization in Streamlit ---
# Initialize session state for vectorstore if it doesn't exist
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# Attempt to load the persisted vector store only if not already loaded or explicitly re-ingested
if st.session_state.vectorstore is None:
    try:
        # Initialize the same embedding model used for ingestion
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Check if the persist directory exists and has data
        # A simple check for existence and non-emptiness
        if os.path.exists(PERSIST_DIRECTORY) and any(os.scandir(PERSIST_DIRECTORY)):
            st.session_state.vectorstore = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=embeddings,
                collection_name=COLLECTION_NAME
            )
            st.success(f"Vector store loaded successfully from {PERSIST_DIRECTORY}!")
        else:
            st.warning(f"No existing vector store found or it's empty at {PERSIST_DIRECTORY}. Please ingest documents first.")
            st.session_state.vectorstore = None # Ensure it's None if not loaded
    except Exception as e:
        st.error(f"Error loading vector store: {e}. Please ensure document ingestion was successful.")
        st.session_state.vectorstore = None


# Button to trigger document ingestion
if st.button("Ingest Documents (Run this if you add/change files)"):
    with st.spinner("Ingesting documents... This might take a moment."):
        if ingest_documents():
            st.success("Documents ingested and vector store updated successfully! You can now ask questions.")
            # Reload the vector store after ingestion to ensure it's up-to-date
            try:
                embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
                st.session_state.vectorstore = Chroma(
                    persist_directory=PERSIST_DIRECTORY,
                    embedding_function=embeddings,
                    collection_name=COLLECTION_NAME
                )
                st.success("Vector store reloaded after ingestion.")
            except Exception as e:
                st.error(f"Error reloading vector store after ingestion: {e}")
        else:
            st.error("Document ingestion failed. Check console and Streamlit messages for details.")

# Only show query input if vector store is loaded
if st.session_state.vectorstore is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_input("Enter your query:", placeholder="Ask about the content in your documents...")
    with col2:
        st.write("")  # Add some vertical space

    if st.button("Get Answer"):
        if user_query:
            with st.spinner("Searching documents and generating answer..."):
                retrieved_document, answer = retrieve_and_generate_with_rag(
                    user_query, 
                    st.session_state.vectorstore, 
                    k=3  # Number of documents to retrieve
                )

            st.subheader("Generated Answer:")
            st.info(answer)

            if retrieved_document:
                with st.expander("See Retrieved Documents"):
                    st.text(retrieved_document) # Use st.text for preformatted text
            else:
                st.warning("No relevant documents were found for this query.")
        else:
            st.warning("Please enter a query to get an answer.")
else:
    st.info("Please ingest documents first by clicking the button above.")

st.markdown("---")
st.markdown("### How this RAG System Works:")
st.markdown(
    f"""
    1.  **Document Ingestion**: Documents from `{DATA_DIRECTORY}` are processed, chunked, and stored in a vector database. You need to click "Ingest Documents" if you add/change files.
    2.  **Query Input**: You enter a question about the content in your documents.
    3.  **Vector Search**: The system searches for the most relevant document chunks using semantic similarity.
    4.  **Response Generation**: Based on the retrieved content, a response is generated (currently showing retrieved content directly).
    
    **Current Status:**
    - Vector Store Location: `{PERSIST_DIRECTORY}`
    - Collection Name: `{COLLECTION_NAME}`
    - Documents Folder: `{DATA_DIRECTORY}`
    
    *Note: This system retrieves actual content from your ingested documents using vector similarity search.*
    """
)