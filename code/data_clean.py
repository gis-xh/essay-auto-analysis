import os
import pandas as pd
import openpyxl


''' 1 设置工作目录
'''
# 定义要创建的目录的路径
workpath = "../data/output"

# 判断目录是否存在，如果不存在则创建
if not os.path.exists (workpath):
    # 创建目录
    os.makedirs (workpath)


''' 2 清洗空列
'''
def clean_null(inputFile):
    # 读取 xls 文件中的数据
    df = pd.read_excel(f'../data/input/{inputFile}')
    # 删除所有全为缺失值的列
    df = df.dropna(axis=1, how='all')
    # 删除只有列名没有数据的列
    df = df.loc[:, (df.notnull().sum() > 0)]
    # 将 &#8208; 和 &#8211; 都替换为 -
    df = df.replace({'&#8208; ': '-', '&#8211; ': '-'}, regex=True)
    # 设置输出的文件名
    outputFile = f'{workpath}/wos_cleaned.xlsx'
    # 将处理过的数据导出到新的 Excel 文件中
    df.to_excel(outputFile, index=False)
    return outputFile

''' 3 核心数据筛选
'''
def coreDataSelect(inputFile):
    # 读取 xlsx 文件中的数据
    inputFile = clean_null(inputFile)
    df = pd.read_excel(inputFile)
    # 筛选出目标表头
    df = df.loc[:, ["Article Title", "Source Title", "Author Keywords",
                    "Keywords Plus", 'Abstract', 'Addresses', 'Affiliations', "Times Cited, All Databases", "Publication Year", 'DOI', 'Research Areas']]
    # 将表头进行翻译
    df.columns=["原文标题", "期刊", "作者关键词", "WOS 关键词", "摘要", "作者地址", "机构", "引用次数", "发表年份", "DOI", "研究领域"]
    outputFile = f'{workpath}/wos_coredata_cleaned.xlsx'
    df.to_excel(outputFile, index=False)
    return outputFile