"""
构建本地知识库:
1. 读取预处理后含有论文相关信息的 xlsx 表格, 先转换成 csv 格式
2. 调用 embedding 模型分割成向量
3. 构建本地的 pg 向量数据库用于存储分割后的向量
"""

import pandas as pd
import config
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 0. 加载相关参数
# embedding = config.op_embedding
embedding = config.hf_embedding
# PGVector 数据库连接字符串
CONNECTION_STRING = config.CONNECTION_STRING
# 集合名称
COLLECTION_NAME = config.COLLECTION_NAME

# 1. 加载指定路径下所有文件
workpath = "data/output"
excel_file = f"{workpath}/wos_coredata_cleaned.xlsx"
csv_file = f"{workpath}/paper_title_abstract.csv"

# 2. xlsx 转 csv


def xlsx2csv():
    # 用pandas.read_excel()读取xlsx文件，并返回一个DataFrame对象
    df = pd.read_excel(excel_file).loc[:, ["Title", 'Abstract']]
    # 用pandas.DataFrame.to_csv()将DataFrame对象写入到csv文件中
    df.to_csv(csv_file, index=False)

# 3， 加载 csv 文件


def load_files():
    loader = CSVLoader(csv_file, source_column="Abstract")
    # loader = UnstructuredExcelLoader(excel_file, mode="elements", unstructured_kwargs={
    #     'Title', 'Abstract'
    # })
    data = loader.load()
    return data


# 4. 分割文本


def split_doc():
    chunk_size = 200  # 设置块大小
    chunk_overlap = 40  # 设置块重叠大小
    # 初始化文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # 设置 换行, 句号, 逗号, 空格 为分隔符 (按顺序切割)
        separators=["\n", "(?<=\. )", ",", " "]
    )
    # 调用分割器分割文本
    data = load_files()
    split_texts = text_splitter.split_documents(data)
    print("分割前:", len(data), "\n分割后:", len(split_texts))
    return split_texts


# 5. 连接向量数据库并创建表


def create_vectorstore():
    split_texts = split_doc()
    vectordb = PGVector.from_documents(
        documents=split_texts,
        embedding=embedding,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )
    return vectordb

create_vectorstore()
