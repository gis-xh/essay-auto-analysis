# 开发记录（三）关键词词频统计



## 1 同类词合并

在使用 pandas 对存储 wos 论文数据的 `*.xlsx` 文件中关键词进行词频统计前，将同义词以及相同含义的专业术语进行合并，从而提升词频统计精确度。

### 1.1 文本预处理

由于 WOS 检索得到论文信息中包含文章关键词和 WOS 关键词，所以需要：

- 首先，将两列关键词的内容进行拼接
- 然后，将每行多个关键词，用分号分割成一个关键词列表
- 接着，并将所有关键词格式化（首字母大写、将括号内的简称全大写、将少于三个字母的单词全大写）
- 最后，返回一个处理好的关键词列表

```python
# 先将关键词列合并，再进行文本预处理，最后返回关键词列表
def all_keywords(inputFile):
    df = pd.read_excel(inputFile)
    # 以分号合并两列关键词内容，并以分号切割成列表，需要注意的是 "; " 而不是 ";"
    keywords = df["作者关键词"].str.cat(sep="; ") + df["WOS 关键词"].str.cat(sep="; ")
    word_list = keywords.split("; ")
    # 判断每个词组是否包含数字，如果包含数字，就保留-，否则就将-替换为空格
    word_list = [w if any(c.isdigit() for c in w) else w.replace("-", " ") for w in word_list]
    # 使用列表推导式和 str.title () 方法将列表中的字符串全部转换为首字母大写
    # str.upper () 全体大写
    word_list_upper = [w.title() for w in word_list]
    # 使用正则表达式匹配括号里的单词，并将其转换为大写
    import re
    word_list_upper = [re.sub(r"\((\w+)\)", lambda m: "(" + m.group(1).upper() + ")", w) for w in word_list_upper]
    # 使用列表推导式和len()函数判断每个单词的长度，并将长度小于等于三的单词转换为大写
    word_list_upper = [w.upper() if len(w) <= 3 else w for w in word_list_upper]
    return word_list_upper
```

### 1.2 同类词合并

#### 1.2.1 建立专业术语映射表

建立一个同义词和专业术语的映射表 (`related_terms.xlsx`)，把不同的表达方式但是意思相同的单词或短语统一为一个标准的词汇，以便于后续的词频统计。表格内容如下：

| Original_Word                     | Mapping_Word                           |
| --------------------------------- | -------------------------------------- |
| GPP                               | Gross Primary Production               |
| Gross Primary Productivity        | Gross Primary Production               |
| Gross Primary Production (GPP)    | Gross Primary Production               |
| Gross Primary Productivity  (GPP) | Gross Primary Production               |
| NPP                               | Net Primary Production                 |
| SIF                               | Solar-Induced Chlorophyll Fluorescence |
| ……                                | ……                                     |

#### 1.2.2 合并同类词

 `pd.merge()` 函数把处理好的关键词列表和映射表进行合并：

- 指定合并方式为左连接（left join），以保留所有原始关键词

- 指定合并依据为原始词（left_on）和映射词（right_on）

```python
# 关键词同义合并，并返回合并后的单词列表
def synonymMerge(inputFile):
    word_list = all_keywords(inputFile)
    # 读取映射表
    df = pd.read_excel("../data/input/related_terms.xlsx")
    mapping_dict = dict(zip(df["Original_Word"], df["Mapping_Word"]))
    # 创建一个空列表用于存储转化后的元素
    transformed_list = []
    # 遍历word_list列表中的每个元素
    for word in word_list:
        # 如果元素在字典中有对应的键，则用字典中的值替换它，否则保持不变
        new_word = mapping_dict.get(word, word)
        # 将转化后的元素添加到新列表中
        transformed_list.append(new_word)    
    # 返回合并后的列表类型的数据
    return transformed_list
```



## 2 词频统计

使用 collections 模块统计词频，并将词频统计结果的前300个词导出成新的excel文档。

```python
def wordCount(inputFile, outputFile):
    # 同义词替换
    word_list = synonymMerge(inputFile)
    # 使用collections进行词频统计，获取前300个高频词及其出现次数
    # 返回一个字典，键为分词，值为出现次数
    word_counts = collections.Counter(word_list)
    # 返回一个列表，每个元素是一个元组，包含分词和出现次数
    word_counts_top300 = word_counts.most_common(300)
    # 将词频统计的结果导出成新的excel文档
    # 创建一个数据框存放列表数据
    df_word_counts = pd.DataFrame(word_counts_top300, columns=["Keyword", "Count"])
    # 导出数据到excel文件，并去掉索引列
    df_word_counts.to_excel(outputFile, index=False)
```





