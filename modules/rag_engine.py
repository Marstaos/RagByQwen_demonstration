from .llm_service import LLMService
from .vector_store import VectorStore

class RAGEngine:
    def __init__(self):
        self.llm_service = LLMService()
        self.vector_store = VectorStore()
        
    def query(self, query_text):
        """使用RAG回答问题，返回检索到的上下文和回答"""
        # 从向量存储中检索相关上下文
        contexts = self.vector_store.similarity_search(query_text)
        
        if not contexts:
            # 如果没有相关上下文，直接使用LLM回答
            messages = [
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": query_text}
            ]
            response = self.llm_service.get_completion(messages)
            
            return {
                "contexts": [],
                "has_context": False,
                "response": response
            }
        else:
            # 将检索到的上下文整合到提示中
            context_text = "\n\n".join(contexts)
            prompt = f"""请基于以下参考信息回答用户的问题。如果参考信息中没有相关内容，请基于你自己的知识回答，并注明这部分是你的知识而非参考信息。

参考信息:
{context_text}

用户问题: {query_text}"""
            
            messages = [
                {"role": "system", "content": "你是一个有帮助的助手。你将根据提供的参考信息回答问题。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用LLM获取回答
            response = self.llm_service.get_completion(messages)
            
            return {
                "contexts": contexts,
                "has_context": True,
                "response": response
            }