import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

'''1. 创建和保存词云图像
'''
def create_wordcloud(word_freq, font_path, output_file):
    wc = WordCloud(
        # width = 300,
        # height = 200,
        background_color = 'white', 
        prefer_horizontal = 1, 
        min_font_size = 2,
        max_font_size = 32,
        font_path = f'../data/fonts/{font_path}', # 使用 f-string 格式化字符串
        scale = 4,
        max_words = 300,
        random_state = 42, # 设置随机状态为一个固定的整数
        colormap = 'viridis' # 指定颜色映射
        # stopwords = STOPWORDS, # 直接传入停用词集合
    ).generate_from_frequencies(word_freq)
    plt.figure(figsize=(12,12), dpi=300)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    wc.to_file(f'../data/output/{output_file}')

'''2. 绘制关键词词云
'''
def keywordCloud(inputFile, lang='en'):
    # 读取 xlsx 文件中的数据
    df = pd.read_excel(inputFile)
    # 将数据转换成字典，键为关键词，值为频数
    word_freq = dict(zip(
        df['Keyword' if lang == 'en' else 'Keyword_Translation'],
        df['Count']
    ))
    # 调用函数，生成英文/中文的词云图像
    wc = create_wordcloud(
        word_freq,
        f'../data/fonts/TIMES.ttf' if lang == 'en' else f'../data/fonts/simsun.ttc',
        f'wos_wordcloud_{lang}.png'
    )