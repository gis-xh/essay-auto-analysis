"""
请在此文件中添加提示词的模板
"""

from langchain.prompts import PromptTemplate


# 1. 提问 Prompt 模板
qa_template = """请你根据下面的已知内容来回答问题。
如果你不知道答案，只需要说不知道，不要试图编造答案。
在回答的最后一定要说 "感谢您的提问！"

已知内容: {context}

问题: {question}
"""
QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=qa_template
)