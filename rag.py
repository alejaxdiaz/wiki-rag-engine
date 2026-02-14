import os
from pathlib import PurePosixPath
from urllib.parse import quote
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

load_dotenv()

INDEX_PATH = "wiki_index"
ORG = os.environ.get("AZURE_DEVOPS_ORG", "")
PROJECT = os.environ.get("AZURE_DEVOPS_PROJECT", "")
WIKI_NAME = f"{PROJECT}.wiki"


def source_to_wiki_url(source: str) -> tuple[str, str]:
    """Convert a local file path to a wiki page name and URL."""
    path = PurePosixPath(source.replace("\\", "/"))
    # Strip the wiki_repo prefix and .md extension
    parts = list(path.parts)
    if parts and parts[0] == "wiki_repo":
        parts = parts[1:]
    name = "/".join(parts)
    if name.endswith(".md"):
        name = name[:-3]
    page_name = name.replace("-", " ")
    page_path = quote("/" + name, safe="/")
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_wiki/wikis/{WIKI_NAME}?pagePath={page_path}"
    return page_name, url

_vectorstore = None
_llm = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        _vectorstore = FAISS.load_local(
            INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
    return _vectorstore


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    return _llm


def search(query: str, k: int = 5) -> list[dict]:
    """Search wiki and return relevant chunks."""
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search_with_score(query, k=k)

    results = []
    for doc, score in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "score": round(1 / (1 + score), 3)
        })
    return results


def ask(query: str) -> dict:
    """Search wiki and generate an answer."""
    results = search(query, k=5)

    if not results:
        return {
            "answer": "I couldn't find any relevant information in the wiki.",
            "sources": []
        }

    context = "\n\n---\n\n".join([
        f"[Source: {r['source']}]\n{r['content']}"
        for r in results
    ])

    prompt = f"""You are a helpful assistant answering questions based on the company wiki.

Rules:
- Answer based ONLY on the provided context
- If the context doesn't contain the answer, say "I couldn't find that in the wiki"
- Be concise and friendly
- Mention which wiki page has more details when relevant

Context:
{context}

Question: {query}

Answer:"""

    llm = get_llm()
    response = llm.invoke(prompt)

    seen = set()
    sources = []
    for r in results:
        if r["source"] not in seen:
            seen.add(r["source"])
            name, url = source_to_wiki_url(r["source"])
            sources.append({"name": name, "url": url})
        if len(sources) >= 3:
            break

    return {
        "answer": response.content,
        "sources": sources
    }