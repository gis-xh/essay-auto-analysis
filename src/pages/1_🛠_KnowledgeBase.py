import streamlit as st

if "PGVECTOR_COLLECTION" not in st.session_state:
    st.session_state["PGVECTOR_COLLECTION"] = ""

st.set_page_config(page_title="知识库设置", layout="wide")

st.title("知识库设置")

collection_name = st.text_input("知识库名称", value=st.session_state["PGVECTOR_COLLECTION"], max_chars=None, key=None, type='default')

saved = st.button("保存")

if saved:
    st.session_state["PGVECTOR_COLLECTION"] = collection_name