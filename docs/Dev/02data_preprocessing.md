# 开发记录（二）数据预处理



## 1 数据清洗

读取从 WOS 检索结果导出的 excel 表，删为空值的列，并且将显示错误的内容批量修正

```sh
def data_cleansing(inputFile, outputFile):
    # 读取 xls 文件中的数据
    df = pd.read_excel(f'../data/input/{inputFile}')
    # 删除所有全为缺失值的列
    df = df.dropna(axis=1, how='all')
    # 删除只有列名没有数据的列
    df = df.loc[:, (df.notnull().sum() > 0)]
    # 将 &#8208; 和 &#8211; 都替换为 -
    df = df.replace({'&#8208; ': '-', '&#8211; ': '-'}, regex=True)
    # 将处理过的数据导出到新的 Excel 文件中
    df.to_excel(outputFile, index=False)
```



## 2 核心数据筛选

将论文的相关核心数据（原文标题，期刊，作者关键词，WOS 关键词，摘要，地址，发表年份，DOI 等）从中筛选出来，导出成新的文件

```python
def coreDataSelect(inputFile, outputFile):
    # 读取 xlsx 文件中的数据
    df = pd.read_excel(inputFile)
    # 筛选出目标表头
    df = df.loc[:, ["Article Title", "Source Title", "Author Keywords",
                    "Keywords Plus", 'Abstract', 'Addresses', "Publication Year", 'DOI']]
    # 将表头进行翻译
    df.columns=["原文标题", "期刊", "作者关键词", "WOS 关键词", "摘要", "地址", "发表年份", "DOI"]
    df.to_excel(outputFile, index=False)
```







