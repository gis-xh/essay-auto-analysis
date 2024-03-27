import os
import re  # 正则表达式
import pandas as pd
import collections
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# 1. 设置工作目录
# 定义要创建的目录的路径
input_path = "../data/input"
output_path = "../data/output"

# 判断目录是否存在，如果不存在则创建
if not os.path.exists(output_path):
    # 创建目录
    os.makedirs(output_path)


class DataClean:
    """
    对 WOS 检索到的论文数据进行数据清洗预处理
    """

    # 1. 清洗空列, 类中的第一个参数是当前所在的对象本身
    def clean_null(self, input_file):
        df = pd.read_excel(f'{input_path}/{input_file}')
        # 删除所有全为缺失值的列
        df = df.dropna(axis=1, how='all')
        # 删除只有列名没有数据的列
        df = df.loc[:, (df.notnull().sum() > 0)]
        # 将错误编码的 &#8208; 和 &#8211; 都替换为 -
        df = df.replace({'&#8208; ': '-', '&#8211; ': '-'}, regex=True)
        # 设置输出的文件名
        output_file = f'{output_path}/wos_cleaned.xlsx'
        df.to_excel(output_file, index=False)
        return output_file

    # 2. 核心数据筛选
    def core_select(self, input_file):
        input_file = self.clean_null(input_file)
        df = pd.read_excel(input_file)
        # 筛选出目标表头
        df = df.loc[:, ["Article Title", "Source Title", "Author Keywords",
                        "Keywords Plus", 'Abstract', 'Addresses', 'Affiliations',
                        "Times Cited, All Databases", "Publication Year", 'DOI', 'Research Areas']]
        # 将表头进行翻译
        df.columns = ["Title", "Source", "Keywords", "WOS_Keywords", "Abstract",
                      "Addresses", "Affiliations", "Cited", "Publication_Year", "DOI", "Research_Areas"]
        output_file = f'{output_path}/wos_coredata_cleaned.xlsx'
        df.to_excel(output_file, index=False)
        return output_file


class KeywordsCount:
    """
    关键词词频统计
    """

    # 将关键词列合并，进行文本预处理，返回关键词列表
    def all_keywords(self, input_file):
        df = pd.read_excel(input_file)
        # 以分号合并两列关键词内容，并以分号切割成列表，需要注意的是 "; " 而不是 ";"
        keywords = df["Keywords"].str.cat(
            sep="; ") + df["WOS_Keywords"].str.cat(sep="; ")
        # keywords = df["作者关键词"].str.cat(sep="; ")
        word_list = keywords.split("; ")
        # 判断每个词组是否包含数字，如果包含数字，就保留-，否则就将-替换为空格
        word_list = [w if any(c.isdigit() for c in w)
                     else w.replace("-", " ") for w in word_list]
        # 使用列表推导式和 str.title () 方法将列表中的字符串全部转换为首字母大写
        # str.upper () 全体大写
        word_list_upper = [w.title() for w in word_list]
        # 使用正则表达式匹配括号里的单词，并将其转换为大写
        word_list_upper = [re.sub(
            r"\((\w+)\)", lambda m: "(" + m.group(1).upper() + ")", w) for w in word_list_upper]
        # 使用列表推导式和len()函数判断每个单词的长度，并将长度小于等于三的单词转换为大写
        word_list_upper = [w.upper() if len(
            w) <= 3 else w for w in word_list_upper]
        return word_list_upper

    # 关键词同义合并，返回合并后的单词列表
    def synonym_merge(self, input_file):
        word_list = self.all_keywords(input_file)
        # 读取映射表
        df = pd.read_excel(f'{input_path}/related_terms.xlsx')
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

    def words_count(self, input_file):
        # 同义词替换
        word_list = self.synonym_merge(input_file)
        # 使用collections进行词频统计，获取前300个高频词及其出现次数
        # 返回一个字典，键为分词，值为出现次数
        word_counts = collections.Counter(word_list)
        # 返回一个列表，每个元素是一个元组，包含分词和出现次数
        word_counts_top100 = word_counts.most_common(100)
        # 将词频统计的结果导出成新的excel文档
        # 创建一个数据框存放列表数据
        df_word_counts = pd.DataFrame(
            word_counts_top100, columns=["Keyword", "Count"])
        output_file = f'{output_path}/keyword_count.xlsx'
        # 导出数据到excel文件，并去掉索引列
        df_word_counts.to_excel(output_file, index=False)
        return output_file


class WordCloudDraw:
    """
    绘制词云图
    """

    # 1. 创建和保存词云图像
    def create_wordcloud(self, word_freq, font_path, output_file):
        wc = WordCloud(
            # width = 300,
            # height = 200,
            background_color='white',
            prefer_horizontal=1,
            min_font_size=2,
            max_font_size=32,
            font_path=f'../data/fonts/{font_path}',  # 使用 f-string 格式化字符串
            scale=4,
            max_words=300,
            random_state=42,  # 设置随机状态为一个固定的整数
            colormap='viridis'  # 指定颜色映射
            # stopwords = STOPWORDS, # 直接传入停用词集合
        ).generate_from_frequencies(word_freq)
        plt.figure(figsize=(12, 12), dpi=300)
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        wc.to_file(f'{output_path}/{output_file}')

    # 2. 绘制关键词词云
    def plt_wordcloud(self, input_file, lang='en'):
        df = pd.read_excel(input_file)
        # 将数据转换成字典，键为关键词，值为频数
        word_freq = dict(zip(
            df['Keyword' if lang == 'en' else 'Keyword_Translation'],
            df['Count']
        ))
        # 调用函数，生成英文/中文的词云图像
        wc = self.create_wordcloud(
            word_freq,
            f'TIMES.ttf' if lang == 'en' else f'simsun.ttc',
            f'wos_wordcloud_{lang}.png'
        )
