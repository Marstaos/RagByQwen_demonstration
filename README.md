# RAG 示范

一个基于检索增强生成（RAG）的智能问答系统。

## 🚀 快速开始

### 环境配置
1. 创建conda环境
```bash
conda create -n rag python=3.9
conda activate rag

```

2. 安装依赖
```bash
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com
pip install -r requirements.txt
```

3. 下载嵌入模型（必需步骤）
```bash
export HF_ENDPOINT=https://hf-mirror.com
python download_models.py
```

### 运行程序
```bash
python main.py
```

## 功能特性
- 支持PDF/TXT/DOCX文档上传与知识库构建
- 基于文本向量的语义检索
- 流式对话交互体验
- 可视化知识库管理
- 支持Qwen大模型API接入

## 📂 项目结构
```
.
├── modules/          # 核心模块
├── ui/               # 用户界面
├── knowledge_base/   # 知识库文档
├── vector_store/     # 向量数据库
├── models/           # 嵌入模型
├── config.py         # 配置文件
└── main.py           # 主程序入口
```