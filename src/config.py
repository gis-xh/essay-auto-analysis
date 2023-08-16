"""
在此文件中进行项目的核心设置
- Eebedding
- LLM
- Vector Store
"""

import os
import openai
import sys
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# 1. 加载 openai 密钥
sys.path.append('../..')
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']

# 2. 加载 OpenAI Embedding 模型
op_embedding = OpenAIEmbeddings()

# 3. 初始化默认的模型
init_llm = "ChatGLM2-6B-int4"
init_embedding_model = "text2vec-base"

# 4. 设置运行模型的设备
EMBEDDING_DEVICE = 'cpu'
LLM_DEVICE = "cpu"

# 5. HuggingFace Embedding 模型字典
embedding_model_dict = {
    # "text2vec-base": "GanymedeNil/text2vec-base-chinese",
    "text2vec-base": "E:/github/LLModels/text2vec-large-chinese",
}

# 6. HuggingFace LLM 模型字典
llm_model_dict = {
    "chatglm": {
        # "ChatGLM-6B-int4": "THUDM/chatglm2-6b-int4",
        "ChatGLM2-6B-int4": "E:/github/LLModels/chatglm2-6b-int4",
    },
}

# 7. 加载 HuggingFace Embedding
hf_embedding = HuggingFaceEmbeddings(
    model_name=embedding_model_dict[init_embedding_model],
    model_kwargs={'device': EMBEDDING_DEVICE},
    encode_kwargs={'normalize_embeddings': False}
)

# 8. 配置向量数据库
# PGVector 数据库连接字符串
CONNECTION_STRING = "postgresql+psycopg2://postgres:123qwe@localhost:4321/essay_anaylsis"
# PGVector 模块将尝试用集合的名称创建一个表.
# 因此, 请确保集合名称是唯一的, 并且用户具有创建表的权限.
COLLECTION_NAME = "llm_langchain_essay"