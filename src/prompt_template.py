"""
请在此文件中添加提示词的模板
"""

from langchain.prompts import PromptTemplate


# 1. 提问 Prompt 模板
qa_template_open = """请你根据下面的已知内容来回答问题。
如果在已知内容中没有相关答案，你可以按照自己的想法进行回答。
在回答的最后一定要说 "感谢您的提问！

已知内容: {context}

问题: {question}
"""

qa_template_custom = """请你根据下面的已知内容来回答问题。
如果你不知道答案，只需要说不知道，不要试图编造答案。
在回答的最后一定要说 "感谢您的提问！"

已知内容: {context}

问题: {question}
"""
QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=qa_template_open
)