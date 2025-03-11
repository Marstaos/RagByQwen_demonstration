import os
import sys
from dotenv import load_dotenv

# 判断是否在打包环境中运行
IN_PACKAGED_ENV = getattr(sys, 'frozen', False)

def get_resource_path(relative_path):
    """获取资源的绝对路径，适用于开发环境和打包后的环境"""
    if IN_PACKAGED_ENV:
        # 如果是打包后的应用程序，使用应用程序所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，使用当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# 加载环境变量(如果有)
load_dotenv()

# API配置
API_KEY = ""  # 移除硬编码的API Key
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"

# 向量模型配置
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"  # 中文向量模型

# 路径配置 - 使用运行时路径函数
KNOWLEDGE_BASE_DIR = get_resource_path("knowledge_base")
VECTOR_STORE_DIR = get_resource_path("vector_store")
MODEL_DIR = get_resource_path("models")

# 确保目录存在
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# 打印调试信息
print(f"知识库目录: {KNOWLEDGE_BASE_DIR}")
print(f"向量存储目录: {VECTOR_STORE_DIR}")
print(f"模型目录: {MODEL_DIR}")

# RAG配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 3