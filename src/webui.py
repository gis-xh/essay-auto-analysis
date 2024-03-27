import gradio as gr
from config import *
from prompt_template import *
from langchain.document_loaders import UnstructuredExcelLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.vectorstores.pgvector import PGVector


# 1. 加载相关参数
# embedding = op_embedding
embedding = hf_embedding
# PGVector 数据库连接字符串
CONNECTION_STRING = CONNECTION_STRING
# 集合名称
COLLECTION_NAME = COLLECTION_NAME
# 构建 Prompt 模板
QA_CHAIN_PROMPT = QA_CHAIN_PROMPT


# 2. 连接已有的向量数据库
def conn_vectorstore():
    store = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embedding_function=embedding,
    )
    return store

db = conn_vectorstore()


# 3. 调用 LLM 生成输出
def llm_predict(question, top_k, temperature, chat_history):
    # 加载模型
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature) 
    
    # 使用矢量数据库作为检索器
    retriever = db.as_retriever(
        # 获取 50 个相关文档以供相似性算法考虑, 但只返回前 k 个, MMR 算法好像有问题
        search_kwargs={'k': top_k, 'fetch_k': 50}
        # search_type="mmr",
        # search_kwargs={'k': top_k}
    )
    # 生成 QA 问答链
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    result = qa_chain({"query": question})
    chat_history.append((question, result["result"]))
    # 预留一个空字符串的输出存放问题的打印
    return "", chat_history


# 4. 向已有向量数据库中添加新的文本数据
def add_files():
    db.add_documents([Document(page_content="foo")])


# 5. 使用 gradio 构建可视化模块
with gr.Blocks() as demo:
    gr.Markdown(
        """
        # <center>论文自动化分析工具 v1.0</center>
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            model_argument = gr.Accordion("模型参数配置")
            with model_argument:
                top_k = gr.Slider(1,
                                    10,
                                    value=6,
                                    step=1,
                                    label="最相关向量数",
                                    interactive=True)

                history_len = gr.Slider(0,
                                        5,
                                        value=3,
                                        step=1,
                                        label="上下文长度",
                                        interactive=True)

                temperature = gr.Slider(0,
                                        1,
                                        value=0.70,
                                        step=0.01,
                                        label="回答灵活度",
                                        interactive=True)

            file = gr.File(label='请上传知识库文件',
                            file_types=['.txt', '.md', '.docx', '.pdf'])

            init_vs = gr.Button("知识库文件向量化")

            gr.Markdown("""提醒：<br>
                1. 使用时请先上传自己的知识文件，并且文件中不含某些特殊字符，否则将返回error. <br>
                2. 也可以加载本地已有的知识库。
                """)

        with gr.Column(scale=3):
            chatbot = gr.Chatbot([], label='Chatbot', height=500)
            message = gr.Textbox(label='请输入相关问题')
            state = gr.State()

            with gr.Row():
                clear_history = gr.ClearButton([message, chatbot], value="🧹 清除历史对话")
                send = gr.Button("🚀 发送")
            
            gr.Examples(["请介绍一下 GPP", "请介绍一下 SIF", "SIF与GPP有什么关系?"], message, cache_examples=False)

        # 回车事件
        message.submit(fn=llm_predict, inputs=[message, top_k, temperature, chatbot], outputs=[message, chatbot])
        # 单击事件
        send.click(fn=llm_predict, 
                   inputs=[message, top_k, temperature, chatbot],
                   outputs=[message, chatbot],
                   api_name="llm_predict")
        
        # init_vs.click(fn=add_files)


if __name__ == "__main__":
    # 在同一局域网络中可以访问
    demo.launch(server_name='0.0.0.0', # 本地设置为 127.0.0.1
                server_port=7860,
                share=True # 本地设为 False
                ) 

# gr.close_all() # 关闭所有 gradio 相关端口
# 