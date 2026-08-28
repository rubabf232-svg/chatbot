# 💬 Chatbot template

A simple Streamlit app that shows how to build a chatbot using OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
# 🤖 My Free RAG Chatbot

An AI-powered chatbot built with **Streamlit, LangChain, Groq, Hugging Face Embeddings, ChromaDB, and DuckDuckGo Search**.

The chatbot can answer questions using uploaded PDF/DOCX documents and can search the internet when the required information is not available in the local knowledge base.

## ✨ Features

* 🤖 AI chatbot powered by Groq
* 📚 RAG-based question answering
* 📄 Supports PDF and DOCX documents
* 🔎 Searches uploaded documents for relevant information
* 🌐 Live internet search when information is not found in documents
* 🧠 Hugging Face embeddings
* 🗄️ ChromaDB vector database
* 💬 Streamlit chat interface
* 🔐 API key stored securely using Streamlit Secrets

## 🛠️ Technologies

* Python
* Streamlit
* LangChain
* Groq
* Hugging Face
* ChromaDB
* DuckDuckGo Search

## 📁 Project Structure

```text
chatbot/
├── streamlit_app.py
├── requirements.txt
├── README.md
├── LICENSE
└── my_documents/
    └── your_documents.pdf
```

## 🔑 API Key Setup

The Groq API key should **not** be stored in the source code.

For Streamlit Cloud, add this in **Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

## ▶️ Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run streamlit_app.py
```

## 📚 Adding Documents

Place your PDF or DOCX files inside:

```text
my_documents/
```

The application will use these documents as its local knowledge base.

## ⚠️ Security

Never upload API keys, passwords, tokens, or other secrets to GitHub.

## 📄 License

This project is licensed under the MIT License.
