import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 2. 加载指定路径下所有文件
workpath = "data/output"
excel_file = f"{workpath}/wos_coredata_cleaned.xlsx"
csv_file = f"{workpath}/paper_title_abstract.csv"


def xlsx2csv():
    # 用pandas.read_excel()读取xlsx文件，并返回一个DataFrame对象
    df = pd.read_excel(excel_file).loc[:, ["Title", 'Abstract']]
    # 用pandas.DataFrame.to_csv()将DataFrame对象写入到csv文件中
    df.to_csv(csv_file, index=False)


def load_files():
    loader = CSVLoader(csv_file, source_column="Abstract")
    # loader = UnstructuredExcelLoader(excel_file, mode="elements", unstructured_kwargs={
    #     'Title', 'Abstract'
    # })
    data = loader.load()
    return data



# 3. 分割文本


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

# 4. 加载 embedding 模型
embedding = OpenAIEmbeddings()

# 5. 连接向量数据库并创建表

# PGVector 数据库连接字符串
CONNECTION_STRING = "postgresql+psycopg2://postgres:123qwe@localhost:4321/essay_anaylsis"
# PGVector 模块将尝试用集合的名称创建一个表.
# 因此, 请确保集合名称是唯一的, 并且用户具有创建表的权限.
COLLECTION_NAME = "llm_langchain_essay"


def create_vectorstore():
    split_texts = split_doc()
    vectordb = PGVector.from_documents(
        documents=split_texts,
        embedding=embedding,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )
create_vectorstore()