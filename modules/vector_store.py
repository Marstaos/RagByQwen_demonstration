import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from config import EMBEDDING_MODEL, VECTOR_STORE_DIR, TOP_K_RETRIEVAL, MODEL_DIR, IN_PACKAGED_ENV

class VectorStore:
    def __init__(self):
        # 设置环境变量，指定模型加载位置
        os.environ['TRANSFORMERS_CACHE'] = MODEL_DIR
        os.environ['HF_HOME'] = MODEL_DIR
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = MODEL_DIR
        
        # 尝试从本地目录加载模型
        model_path = os.path.join(MODEL_DIR, EMBEDDING_MODEL.replace('/', '_'))
        if os.path.exists(model_path):
            print(f"从本地路径加载模型: {model_path}")
            self.embedding_model = SentenceTransformer(model_path)
        else:
            print(f"从Hugging Face加载模型: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        self.index_file = os.path.join(VECTOR_STORE_DIR, "faiss_index.bin")
        self.texts_file = os.path.join(VECTOR_STORE_DIR, "texts.pkl")
        self.index = None
        self.texts = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """加载或创建FAISS索引"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.texts_file):
                self.index = faiss.read_index(self.index_file)
                with open(self.texts_file, 'rb') as f:
                    self.texts = pickle.load(f)
            else:
                # 创建一个空的索引，使用内积计算相似度（适用于余弦相似度）
                dimension = self.embedding_model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatIP(dimension)  # 使用内积而不是L2距离
                self.texts = []
                
                # 如果是打包环境，立即保存空索引，确保文件存在
                if IN_PACKAGED_ENV:
                    self._save_index()  # 修正：使用_save_index而不是save
        except Exception as e:
            print(f"加载索引时出错: {e}")
            # 创建一个空的索引
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)
            self.texts = []
            
            # 保存空索引
            self._save_index()  # 修正：使用_save_index而不是save
    
    def add_texts(self, texts, source_name):
        """添加文本到向量存储"""
        if not texts:
            print("警告: 没有文本内容可添加")
            return
            
        print(f"正在添加 {len(texts)} 个文本片段到向量存储...")
        
        # 为每个文本片段添加来源信息
        texts_with_source = [f"来源: {source_name}\n\n{text}" for text in texts]
        
        # 获取嵌入
        print("生成文本嵌入向量...")
        embeddings = self.embedding_model.encode(texts_with_source)
        print(f"成功生成 {len(embeddings)} 个嵌入向量")
        
        # 添加到FAISS索引
        self.index.add(np.array(embeddings).astype('float32'))
        print(f"向量已添加到索引，当前索引包含 {self.index.ntotal} 个向量")
        
        # 保存文本
        self.texts.extend(texts_with_source)
        
        # 保存索引和文本
        self._save_index()
        print("索引和文本已保存到磁盘")
        
        return True
    
    def similarity_search(self, query, top_k=TOP_K_RETRIEVAL, threshold=0.75):
        """搜索最相似的文档"""
        if not self.texts or self.index.ntotal == 0:
            print("警告: 向量存储为空，无法执行搜索")
            return []
            
        print(f"执行相似度搜索，查询: '{query}'")
        
        # 编码查询
        query_embedding = self.embedding_model.encode([query])
        
        # 搜索
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k=top_k)
        
        # 获取结果并根据相似度阈值筛选
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.texts):
                # 对于内积距离，值越大表示越相似
                similarity_score = dist  # 对于IndexFlatIP，直接使用距离作为相似度
                
                # 提取来源信息，避免在f-string中使用反斜杠
                source_text = self.texts[idx]
                source = source_text.split("\n\n")[0] if "\n\n" in source_text else "未知"
                
                if similarity_score >= threshold:
                    results.append(self.texts[idx])
                    print(f"  结果 {i+1}: 相似度={similarity_score:.4f}, {source}")
                else:
                    print(f"  结果 {i+1}: 相似度={similarity_score:.4f} < {threshold}，被过滤, {source}")
        
        print(f"搜索完成，找到 {len(results)} 个相关文档")
        
        return results
    
    def _save_index(self):
        """保存索引和文本到磁盘"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
            
            # 打印调试信息
            print(f"正在保存索引到: {self.index_file}")
            print(f"正在保存文本到: {self.texts_file}")
            
            # 保存索引
            faiss.write_index(self.index, self.index_file)
            
            # 保存文本
            with open(self.texts_file, 'wb') as f:
                pickle.dump(self.texts, f)
            
            # 验证文件是否已创建
            if os.path.exists(self.index_file) and os.path.exists(self.texts_file):
                print(f"索引和文本文件已成功保存")
                print(f"索引文件大小: {os.path.getsize(self.index_file)} 字节")
                print(f"文本文件大小: {os.path.getsize(self.texts_file)} 字节")
            else:
                print(f"警告: 文件保存后无法验证其存在")
                
            return True
        except Exception as e:
            print(f"保存索引时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear(self):
        """清空向量存储"""
        dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(dimension)  # 使用内积而不是L2距离
        self.texts = []
        self._save_index()