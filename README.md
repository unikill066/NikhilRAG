# NikhilRAG

> A lightweight Streamlit Resume Chatbot powered by Retrieval‑Augmented Generation (RAG)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

NikhilRAG is a GPT-powered RAG chatbot that answers questions about my skills & experience, and, logs queries to database for refinement.

🌐 **Live demo:** [nikhilrag-streamlit.app](https://nikhilrag-ntbaxj9puvp37yaqvkqsiu.streamlit.app/)

![NikhilRAG DEMO](misc/NikhilRAG_demo.gif)

## Quick-start

### 1. Clone & install

```bash
git clone https://github.com/unikill066/NikhilRAG.git
cd NikhilRAG
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
```

### 2. Set environment variables

Create a **`.env`** file (auto‑loaded by *python‑dotenv*) or export them in your shell:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="lsd2_pt_adf...."
LANGSMITH_PROJECT="project"
OPENAI_API_KEY=sk-...
# --- Optional: only if you want Firestore logging ---
GOOGLE_PROJECT_ID=your‑gcp‑project
GOOGLE_CLIENT_EMAIL=service‑acct@your‑gcp‑project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"  # convert .json to base64 format
```

### 3. Run locally

```bash
streamlit run streamlit_app.py
```

On the first launch the app builds a vector index from the files in **`data/`** (~ 5 s). Subsequent boots reuse the cached **`vectordb/`** folder for a < 1 s cold‑start.


## Features

* Conversational Q\&A over a resume, CSV Q‑and‑A pairs, PDF and a Markdown bio
* FAISS vector store with OpenAI **text‑embedding‑3‑small** embeddings
* ChatGPT (**gpt‑3.5‑turbo** by default) via LangChain `ConversationalRetrievalChain`
* Conversation analytics written to **Firebase Firestore** and **LangSmith**
* One‑click deploy to **Streamlit Community Cloud**

## Repository layout

```text
.
├── streamlit_app.py          # Main Streamlit UI & RAG pipeline
├── constants.py              # Model names, paths, Streamlit config
├── data/
│   ├── Nikhil.pdf            # Resume
│   ├── Nikhil.csv            # Q‑and‑A pairs
│   └── Nikhil.md             # Short bio
├── prompt/template.json      # System & QA templates for the LLM
├── vectordb/                 # Pre‑built FAISS / Chroma stores (optional)
├── bin                       # binaries
├── utils                     # utility funcions
├── .env                      # environment variables
├── requirements.txt          # dependencies
└── README.md                 # this file
```



## Configuration

All tunables live in **`constants.py`**:

| name              | default                    | purpose                               |
| ----------------- | -------------------------- | ------------------------------------- |
| `EMBEDDING_MODEL` | `"text-embedding-3-small"` | OpenAI embeddings                     |
| `LLM_MODEL`       | `"gpt-3.5-turbo"`          | Chat completion model                 |
| `CHUNK_SIZE`      | `400`                      | Character chunk length for embeddings |
| `CHUNK_OVERLAP`   | `40`                       | Overlap between chunks                |
| `VECTOR_STORE`    | `"faiss"`                  | Change to `"chroma"` if preferred     |

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (private or public).
2. On [https://streamlit.io/cloud](https://streamlit.io/cloud), click **New app** → choose this repo.
3. Add `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `LANGSMITH_API_KEY` (and Firebase keys) in **Secrets**.
4. Hit **Deploy** – done, your app is live on ☁️


## Rebuilding the vector store

Delete the **`vectordb/`** directory:

```bash
python streamlit_app.py
```

## License

Licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## Acknowledgements and References
- [LangChain](https://python.langchain.com/)
- [Firebase](https://firebase.google.com/)
- [LangSmith](https://smith.langchain.com/)
- [LangChain Prompt Templates](https://lagnchain.readthedocs.io/en/latest/modules/prompts/prompt_templates/getting_started.html)
- [resumeGPT](https://github.com/kredar/resumeGPT?tab=readme-ov-file)
- [FAISS](https://faiss.ai/)
- [Streamlit](https://streamlit.io/)
- [Streamlit Secrets](https://docs.streamlit.io/develop/api-reference/connections/st.secrets)
- [Github Documentation](https://github.com/Wytamma/write-the-code)