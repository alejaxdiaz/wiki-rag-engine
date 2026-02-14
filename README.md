# Azure DevOps Wiki RAG Assistant

A Python RAG (Retrieval-Augmented Generation) application that indexes your Azure DevOps Wiki into a FAISS vector store and provides a Streamlit-based chat interface for intelligent question answering.

## Features

- **Automated Wiki Indexing**: Clones/pulls your Azure DevOps wiki repository and creates a searchable vector index
- **Smart Search**: Uses OpenAI embeddings and FAISS for semantic search across all wiki pages
- **AI-Powered Answers**: GPT-4o-mini generates grounded answers based only on wiki content
- **Source Attribution**: Every answer includes direct links to the source wiki pages
- **Interactive UI**: Streamlit web interface with chat and debug modes
- **Markdown-Aware**: Intelligently chunks Markdown documents for better context

## Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Azure DevOps account with wiki access
- Azure DevOps Personal Access Token with Code (Read) permissions

## Quick Start

### 1. Clone this repository

```bash
git clone <your-repo-url>
cd rag
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_DEVOPS_PAT=your-personal-access-token
AZURE_DEVOPS_ORG=your-organization-name
AZURE_DEVOPS_PROJECT=YourProjectName
```

**How to get Azure DevOps PAT:**
1. Go to `https://dev.azure.com/{YOUR_ORG}/_usersSettings/tokens`
2. Click "New Token"
3. Give it a name and set expiration
4. Under "Scopes", select "Code" → "Read"
5. Copy the token immediately (you won't see it again)

### 5. Index your wiki

```bash
python indexer.py
```

This will:
- Clone your Azure DevOps wiki repository
- Load all `.md` files (excluding `.attachments/`)
- Split them into 1000-character chunks with 100-character overlap
- Create embeddings using OpenAI's `text-embedding-3-small`
- Save the FAISS index to `./wiki_index/`

**Note:** First-time indexing can take a few minutes depending on wiki size.

### 6. Run the web app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Chat Tab

Ask questions about your wiki in natural language:

```
Q: How do we deploy to production?
A: According to the deployment guide, production deployments require...
📄 Deployment-Guide | CI-CD-Pipeline
```

The assistant:
- Answers only based on indexed wiki content
- Provides direct links to source pages
- Says "I couldn't find that in the wiki" when info isn't available

### Search Debug Tab

Inspect raw search results to understand what chunks are being retrieved:
- View similarity scores
- See exact chunk content
- Identify which wiki pages are matching

## Architecture

### Data Flow

```
Azure DevOps Wiki → indexer.py → ./wiki_index/ (FAISS) → rag.py → app.py
```

### Modules

- **[indexer.py](indexer.py)** — Data pipeline that clones the wiki, loads documents, and builds the FAISS index
- **[rag.py](rag.py)** — Retrieval engine with `search()` for raw results and `ask()` for LLM-generated answers
- **[app.py](app.py)** — Streamlit UI with chat and debug interfaces

### Technical Details

- **Embeddings**: OpenAI `text-embedding-3-small`
- **LLM**: OpenAI `gpt-4o-mini` (temperature: 0.3)
- **Vector Store**: FAISS (local files)
- **Chunking**: 1000 chars, 100 overlap, Markdown-aware splitter
- **Batch Processing**: 100 chunks per batch during indexing

## Configuration

All configuration is via environment variables in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxx...` |
| `AZURE_DEVOPS_PAT` | Personal Access Token | `abc123...` |
| `AZURE_DEVOPS_ORG` | Azure DevOps organization | `mycompany` |
| `AZURE_DEVOPS_PROJECT` | Project name | `MyProject` |

The wiki name is automatically derived as `{PROJECT}.wiki`.

## Project Structure

```
.
├── indexer.py           # Wiki indexing pipeline
├── rag.py               # RAG retrieval and generation
├── app.py               # Streamlit web interface
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── CLAUDE.md           # AI assistant instructions
└── README.md           # This file

# Generated (git-ignored)
├── wiki_repo/          # Cloned wiki repository
└── wiki_index/         # FAISS vector index
```

## Re-indexing

To update the index with latest wiki changes:

```bash
python indexer.py
```

The script will pull the latest changes from the wiki repository and rebuild the index.

## Troubleshooting

### "Index not found" error

Run `python indexer.py` first to create the index.

### Authentication errors

- Verify your `AZURE_DEVOPS_PAT` has Code (Read) permissions
- Check that `AZURE_DEVOPS_ORG` and `AZURE_DEVOPS_PROJECT` are correct
- Ensure your PAT hasn't expired

### Empty or wrong answers

- Re-run indexing: `python indexer.py`
- Try the Search Debug tab to see what chunks are being retrieved
- Check if the information actually exists in your wiki

### OpenAI API errors

- Verify your `OPENAI_API_KEY` is valid
- Check you have sufficient API credits
- Ensure you have access to `text-embedding-3-small` and `gpt-4o-mini`

## Customization

### Change chunk size

Edit [indexer.py:62-65](indexer.py#L62-L65):

```python
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.MARKDOWN,
    chunk_size=1000,  # Adjust this
    chunk_overlap=100  # And this
)
```

### Change LLM model or temperature

Edit [rag.py:48](rag.py#L48):

```python
_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
```

### Modify the prompt

Edit [rag.py:82-95](rag.py#L82-L95) to change how the assistant responds.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
