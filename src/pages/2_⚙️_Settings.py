import config
import streamlit as st

if "TOP_K" not in st.session_state:
    st.session_state["TOP_K"] = ""
if "HISTORY_LEN" not in st.session_state:
    st.session_state["HISTORY_LEN"] = ""
if "TEMPERATURE" not in st.session_state:
    st.session_state["TEMPERATURE"] = ""

st.set_page_config(page_title="模型参数设置", layout="wide")

st.title("模型参数设置")

top_k = st.slider("最相关向量数",
                  1,
                  10,
                  value=6,
                  step=1)

history_len = st.slider("上下文长度",
                        0,
                        5,
                        value=3,
                        step=1)

temperature = st.slider("回答灵活度",
                        0.0,
                        1.0,
                        value=0.7,
                        step=0.01)

saved = st.button("保存")

if saved:
    st.session_state["TOP_K"] = top_k
    st.session_state["HISTORY_LEN"] = history_len
    st.session_state["TEMPERATURE"] = temperature