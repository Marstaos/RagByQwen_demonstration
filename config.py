import os
from dotenv import load_dotenv

# 加载环境变量(如果有)
load_dotenv()

# API配置
API_KEY = ""  # 移除硬编码的API Key
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

# 向量模型配置
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"  # 中文向量模型

# 路径配置
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store")
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# 确保目录存在
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# RAG配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 3