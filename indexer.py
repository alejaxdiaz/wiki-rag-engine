import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# Config
PAT = os.environ.get("AZURE_DEVOPS_PAT")
ORG = os.environ.get("AZURE_DEVOPS_ORG")
PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT")

if not all([PAT, ORG, PROJECT]):
    raise ValueError("Set AZURE_DEVOPS_PAT, AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT in .env")

WIKI_NAME = f"{PROJECT}.wiki"
CLONE_URL = f"https://{PAT}@dev.azure.com/{ORG}/{PROJECT}/_git/{WIKI_NAME}"
REPO_PATH = "./wiki_repo"
INDEX_PATH = "./wiki_index"


def clone_wiki():
    """Clone or pull the wiki repo."""
    if Path(REPO_PATH).exists():
        print("Pulling latest changes...")
        repo = Repo(REPO_PATH)
        repo.remotes.origin.pull()
    else:
        print("📥 Cloning wiki...")
        Repo.clone_from(CLONE_URL, REPO_PATH)
    print("✅ Wiki repo ready")


def load_documents():
    """Load all markdown files from the wiki."""
    print("📄 Loading documents...")

    loader = DirectoryLoader(
        REPO_PATH,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True
    )

    docs = loader.load()
    docs = [d for d in docs if ".attachments" not in d.metadata.get("source", "")]

    print(f"✅ Loaded {len(docs)} documents")
    return docs


def split_documents(docs):
    """Split documents into chunks."""
    print("✂️ Splitting documents...")

    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)
    print(f"✅ Created {len(chunks)} chunks")
    return chunks


def create_index(chunks):
    """Create FAISS vector index."""
    print("🔢 Creating embeddings (this may take a while)...")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    batch_size = 100
    vectorstore = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"   Processing {i + len(batch)}/{len(chunks)} chunks...")

        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            batch_store = FAISS.from_documents(batch, embeddings)
            vectorstore.merge_from(batch_store)

    vectorstore.save_local(INDEX_PATH)
    print(f"✅ Index saved to '{INDEX_PATH}'")


def build_index():
    """Full indexing pipeline."""
    clone_wiki()
    docs = load_documents()
    chunks = split_documents(docs)
    create_index(chunks)
    print("\n🎉 Done! You can now run: streamlit run app.py")


if __name__ == "__main__":
    build_index()