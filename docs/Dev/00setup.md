# WOS 论文自动化分析工具环境配置



## 1 虚拟环境配置

### 1.1 创建虚拟环境

```sh
conda create -n essay_auto python=3.9 -y
```

### 1.2 激活虚拟环境

```sh
conda activate essay_auto
```



## 2 安装相关包

### 2.1 安装基础开发环境

```sh
pip install jupyterlab pandas
```

### 2.2 安装 excel 交互包

```sh
pip install xlrd openpyxl
```

### 2.3 安装可视化包

安装 `matplotlib` 、词云包与 `pyecharts` 包，用于数据的可视化分析

```sh
pip install matplotlib wordcloud pyecharts
```

### 2.4 安装翻译包

安装腾讯云 python SDK 的 `tencentcloud-sdk-python` 模块

```sh
pip install tencentcloud-sdk-python
```



## 3 环境备份

### 3.1 备份虚拟环境

```sh
conda env export -n essay_auto > essay_auto_env.yaml
```

- `-n` 后面的参数是待克隆的环境名称

### 3.2 克隆虚拟环境

```sh
conda env create -n essay_auto -f essay_auto_env.yaml
```

- `-n` 后的参数是克隆后的虚拟环境名称
- `-f` 后参数指的是 `*.yaml` 环境内容


