# 开发记录（五）关键词词云可视化



## 1 模块介绍

在对关键词进行 合并、首字母大写、词频统计、翻译等一系列处理后，使用词云包与 `pyecharts` 包来实现关键词词云图的显示。



## 2 词云图绘制

### 2.1 创建和保存词云图像

```python
def create_wordcloud(word_freq, font_path, output_file):
    wc = WordCloud(
        # width = 300,
        # height = 200,
        background_color = 'white', 
        prefer_horizontal = 1, 
        min_font_size = 1,
        font_path = f'./fonts/{font_path}', # 使用 f-string 格式化字符串
        scale = 4,
        max_words = 300
        # stopwords = STOPWORDS, # 直接传入停用词集合
        # colormap = 'viridis' # 指定颜色映射
    ).generate_from_frequencies(word_freq)
    plt.figure(figsize=(6,6), dpi=300)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    wc.to_file(f'./output/{output_file}')
```



### 2.2 绘制关键词词云

这里默认为英文词云，中文词云需要另行设置。

```python
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
        'times.ttf' if lang == 'en' else 'simsun.ttc',
        f'wordcloud_{lang}.png'
    )
```



