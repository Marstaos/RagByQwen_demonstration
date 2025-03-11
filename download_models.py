import os
import shutil
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from config import MODEL_DIR, EMBEDDING_MODEL

def download_models():
    """预下载所有需要的模型到本地目录"""
    print(f"开始下载模型: {EMBEDDING_MODEL}")
    
    # 确保目录存在
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 设置环境变量（让Hugging Face知道从哪里加载和保存模型）
    os.environ['TRANSFORMERS_CACHE'] = MODEL_DIR
    os.environ['HF_HOME'] = MODEL_DIR
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = MODEL_DIR
    
    # 使用原始的huggingface模型下载（更可靠）
    print("下载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    print("下载model...")
    model = AutoModel.from_pretrained(EMBEDDING_MODEL)
    
    # 也加载SentenceTransformer版本以确保完整性
    print("加载SentenceTransformer...")
    st_model = SentenceTransformer(EMBEDDING_MODEL)
    
    # 确保模型被正确保存
    print("保存模型...")
    model_save_path = os.path.join(MODEL_DIR, EMBEDDING_MODEL.replace('/', '_'))
    os.makedirs(model_save_path, exist_ok=True)
    
    # 手动保存模型
    tokenizer.save_pretrained(model_save_path)
    model.save_pretrained(model_save_path)
    
    # 确保SentenceTransformer能找到这个模型
    st_model.save(model_save_path)
    
    print(f"\n模型已成功下载并保存到: {MODEL_DIR}")
    print("模型文件列表:")
    
    # 打印目录内容
    model_files_found = False
    for root, dirs, files in os.walk(MODEL_DIR):
        for file in files:
            model_files_found = True
            print(os.path.join(root, file))
    
    if not model_files_found:
        print("警告: 未找到模型文件! 模型可能下载失败或保存在其他位置。")
        # 检查默认位置
        default_cache = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        print(f"检查默认缓存位置: {default_cache}")
        if os.path.exists(default_cache):
            print("找到默认缓存，正在尝试复制模型文件...")
            # 查找默认位置的模型文件
            model_name_parts = EMBEDDING_MODEL.split('/')[-1]
            for root, dirs, files in os.walk(default_cache):
                if model_name_parts in root:
                    print(f"找到可能的模型文件夹: {root}")
                    # 复制到我们的目录
                    dest_dir = os.path.join(MODEL_DIR, os.path.basename(root))
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir, exist_ok=True)
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dest_dir, file)
                        print(f"复制: {src_file} -> {dst_file}")
                        shutil.copy2(src_file, dst_file)

if __name__ == "__main__":
    download_models()