# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python RAG (Retrieval-Augmented Generation) application that indexes an Azure DevOps Wiki into a FAISS vector store and provides a Streamlit-based chat interface for question answering.

## Commands

```bash
# Install dependencies (use the existing venv)
pip install -r requirements.txt

# Index the wiki (clones/pulls from Azure DevOps, builds FAISS index)
python indexer.py

# Run the Streamlit web app
streamlit run app.py
```

There are no test or lint commands configured.

## Architecture

Three-module pipeline with singleton patterns:

- **indexer.py** — Data pipeline: clones Azure DevOps wiki repo via PAT auth, loads `.md` files (excluding `.attachments/`), splits into 1000-char chunks (100 overlap) using Markdown-aware splitter, creates FAISS index in batches of 100, saves to `./wiki_index/`.
- **rag.py** — Retrieval engine: lazy-loads FAISS index and GPT-4o-mini as module-level singletons. `search()` returns top-K chunks with normalized similarity scores. `ask()` builds a grounded prompt from retrieved chunks and returns the LLM answer with source attribution.
- **app.py** — Streamlit UI with two tabs: Chat (multi-turn conversation with sources) and Search Debug (raw chunk inspection with similarity scores).

Data flow: Azure DevOps Wiki → `indexer.py` → `./wiki_index/` (FAISS) → `rag.py` → `app.py`

## Configuration

Environment variables in `.env` (copy from `.env.example`):
- `OPENAI_API_KEY` — OpenAI API key (embeddings + chat)
- `AZURE_DEVOPS_PAT` — Personal Access Token for wiki repo access (Code Read permission)
- `AZURE_DEVOPS_ORG` — Azure DevOps organization name
- `AZURE_DEVOPS_PROJECT` — Project name (wiki name is derived as `{PROJECT}.wiki`)

Generated local directories (git-ignored):
- `./wiki_repo/` — Cloned wiki repository
- `./wiki_index/` — FAISS vector store files
