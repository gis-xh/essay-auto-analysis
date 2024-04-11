# WOS 论文自动化分析工具环境配置



## 1 虚拟环境配置

### 1.1 创建虚拟环境

```sh
conda create -n paper_auto python=3.9 -y
```

### 1.2 激活虚拟环境

```sh
conda activate paper_auto
```



## 2 安装相关包

### 2.1 检查本机 CUDA 环境

```
# 检查 nvidia 显卡环境
nvidia-smi
# 检查 CUDA 安装情况
nvcc -V
```

### 2.2 安装 PyTorch 环境

- 选择本机安装的 CUDA 版本号，使用 torch2.0-GPU CUDA 必须使用 11.8 或更高版本

```sh
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/CUDA版本
```

### 2.3 安装相关工具包

```sh
pip install -r requirements.txt
```



## 3 环境备份

### 3.1 备份虚拟环境

```sh
conda env export -n paper_auto > paper_auto.yaml
```

- `-n` 后面的参数是待克隆的环境名称

### 3.2 克隆虚拟环境

```sh
conda env create -n paper_auto -f paper_auto.yaml
```

- `-n` 后的参数是克隆后的虚拟环境名称
- `-f` 后参数指的是 `*.yaml` 环境内容

