import os

import streamlit as st
from langchain_community.document_loaders import (
    PyPDFDirectoryLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from duckduckgo_search import DDGS


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Free AI Bot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 My Free RAG Chatbot")

st.caption(
    "AI Assistant using Groq, local documents, "
    "and live internet search"
)


# ============================================================
# 2. GET GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = ""

if not GROQ_API_KEY:
    st.error("❌ Groq API key is missing.")
    st.info(
        "Add GROQ_API_KEY to Streamlit Secrets."
    )
    st.stop()


# ============================================================
# 3. FOLDERS
# ============================================================

DATA_FOLDER = "./my_documents"
DB_FOLDER = "./chroma_db"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)


# ============================================================
# 4. LOAD DOCUMENTS AND CREATE RAG
# ============================================================

@st.cache_resource
def initialize_rag():

    documents = []

    # --------------------------------------------------------
    # Load PDF files
    # --------------------------------------------------------

    try:
        pdf_loader = PyPDFDirectoryLoader(DATA_FOLDER)
        pdf_documents = pdf_loader.load()
        documents.extend(pdf_documents)

    except Exception as e:
        st.warning(f"PDF loading error: {e}")

    # --------------------------------------------------------
    # Load DOCX files
    # --------------------------------------------------------

    try:
        for file in os.listdir(DATA_FOLDER):

            if file.lower().endswith(".docx"):

                docx_path = os.path.join(
                    DATA_FOLDER,
                    file
                )

                docx_loader = Docx2txtLoader(
                    docx_path
                )

                docx_documents = docx_loader.load()
                documents.extend(docx_documents)

    except Exception as e:
        st.warning(f"DOCX loading error: {e}")

    # --------------------------------------------------------
    # Check documents
    # --------------------------------------------------------

    if not documents:
        return None

    # --------------------------------------------------------
    # Split documents
    # --------------------------------------------------------

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    final_chunks = text_splitter.split_documents(
        documents
    )

    # --------------------------------------------------------
    # HuggingFace Embeddings
    # --------------------------------------------------------

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # --------------------------------------------------------
    # Chroma Vector Database
    # --------------------------------------------------------

    vector_store = Chroma.from_documents(
        documents=final_chunks,
        embedding=embeddings,
        persist_directory=DB_FOLDER,
    )

    # --------------------------------------------------------
    # Retriever
    # --------------------------------------------------------

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 2}
    )

    return retriever


retriever = initialize_rag()


# ============================================================
# 5. GROQ AI MODEL
# ============================================================

llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY,
)


# ============================================================
# 6. LIVE INTERNET SEARCH
# ============================================================

def live_internet_search(query):

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=3,
                )
            )

            if results:

                text_results = []

                for result in results:

                    body = result.get(
                        "body",
                        ""
                    )

                    if body:
                        text_results.append(body)

                if text_results:

                    return "\n\n".join(
                        text_results
                    )

    except Exception:

        return (
            "Internet search is currently unavailable."
        )

    return "No internet context available."


# ============================================================
# 7. GENERATE SMART RESPONSE
# ============================================================

def generate_smart_response(user_query):

    context = ""

    source_used = "🧠 AI Background Knowledge"

    # --------------------------------------------------------
    # Search uploaded files
    # --------------------------------------------------------

    if retriever:

        try:

            matched_docs = retriever.invoke(
                user_query
            )

            if matched_docs:

                context = "\n\n".join(
                    [
                        doc.page_content
                        for doc in matched_docs
                    ]
                )

        except Exception:

            context = ""

    # --------------------------------------------------------
    # Ask Groq whether files contain the answer
    # --------------------------------------------------------

    decision_prompt = f"""
User question:

{user_query}


Available document context:

{context}


Does the available document context contain
the exact and sufficient answer to the user's question?

Reply with ONLY:

YES

or

NO
"""

    try:

        decision_response = llm.invoke(
            decision_prompt
        )

        decision = (
            decision_response.content
            .strip()
            .upper()
        )

    except Exception as e:

        return (
            f"❌ Groq API error: {e}",
            "⚠️ Error",
        )

    # --------------------------------------------------------
    # If answer is NOT in files → Internet
    # --------------------------------------------------------

    if not decision.startswith("YES"):

        with st.spinner(
            "🔍 Answer not found in files. "
            "Searching the internet..."
        ):

            internet_result = (
                live_internet_search(
                    user_query
                )
            )

            context = (
                "Live Internet Search Results:\n\n"
                + internet_result
            )

            source_used = (
                "🌐 Live Internet Search"
            )

    else:

        source_used = (
            "📁 Uploaded Local Files"
        )

    # --------------------------------------------------------
    # Final AI prompt
    # --------------------------------------------------------

    final_prompt = f"""
You are a helpful and friendly AI assistant.

Answer the user's question clearly and accurately.

Use the provided context when it is relevant.

Do not invent information that is not supported
by the context.

Context:

{context}


Question:

{user_query}


Give a clear answer in English.
"""

    try:

        response = llm.invoke(
            final_prompt
        )

        ai_response = response.content

    except Exception as e:

        ai_response = (
            f"❌ Error generating response: {e}"
        )

        source_used = "⚠️ Error"

    return ai_response, source_used


# ============================================================
# 8. CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# 9. CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a question here..."
)


if user_input:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_input
        )

    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        response_text, source = (
            generate_smart_response(
                user_input
            )
        )

        st.markdown(
            response_text
        )

        st.caption(
            f"ℹ️ Source Used: {source}"
        )

    # --------------------------------------------------------
    # Save AI response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_text,
        }
    )
