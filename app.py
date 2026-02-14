import streamlit as st
from dotenv import load_dotenv
from rag import ask, search

load_dotenv()

st.set_page_config(page_title="Wiki Assistant", page_icon="📚", layout="centered")

st.title("📚 Wiki Assistant")
st.caption("Test your RAG setup against the Azure DevOps wiki")

tab1, tab2 = st.tabs(["💬 Chat", "🔍 Search Debug"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                links = " | ".join([f"[{s['name']}]({s['url']})" for s in msg["sources"]])
                st.caption("📄 " + links, unsafe_allow_html=False)

    if query := st.chat_input("Ask something about the wiki..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = ask(query)
            st.markdown(result["answer"])
            if result["sources"]:
                links = " | ".join([f"[{s['name']}]({s['url']})" for s in result["sources"]])
                st.caption("📄 " + links, unsafe_allow_html=False)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"]
        })

with tab2:
    st.subheader("Search Debug Mode")
    st.caption("See exactly what chunks are retrieved for a query")

    debug_query = st.text_input("Enter a search query:")
    k = st.slider("Number of results", 1, 10, 5)

    if debug_query:
        with st.spinner("Searching..."):
            results = search(debug_query, k=k)

        for i, r in enumerate(results, 1):
            with st.expander(f"Result {i} | Score: {r['score']} | {r['source']}"):
                st.text(r["content"])