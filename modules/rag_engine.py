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
                {"role": "system", "content": "你是尊敬的马斯陶哥哥为乐乐独家打造的大模型 lele1.0，作为一个RAG教学项目，用于乐乐学习之用。"},
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
                {"role": "system", "content": "你是尊敬的马斯陶哥哥为乐乐独家打造的大模型 lele1.0，作为一个RAG教学项目，用于乐乐学习之用。你将根据提供的参考信息回答问题。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用LLM获取回答
            response = self.llm_service.get_completion(messages)
            
            return {
                "contexts": contexts,
                "has_context": True,
                "response": response
            }
            
    def stream_query(self, query_text, callback):
        """使用RAG流式回答问题
        
        Args:
            query_text: 用户查询文本
            callback: 每次收到流式内容时的回调函数，接收参数(content_delta, is_done)
        
        Returns:
            dict: 包含上下文信息的字典
        """
        # 从向量存储中检索相关上下文
        contexts = self.vector_store.similarity_search(query_text)
        
        if not contexts:
            # 如果没有相关上下文，直接使用LLM回答
            messages = [
                {"role": "system", "content": "你是尊敬的马斯陶哥哥为乐乐独家打造的大模型 lele1.0，作为一个RAG教学项目，用于乐乐学习之用。你需要用温柔活泼的语气回答用户的问题。"},
                {"role": "user", "content": query_text}
            ]
            self.llm_service.get_streaming_completion(messages, callback)
            
            return {
                "contexts": [],
                "has_context": False
            }
        else:
            # 将检索到的上下文整合到提示中
            context_text = "\n\n".join(contexts)
            prompt = f"""请基于以下参考信息回答用户的问题。如果参考信息中没有相关内容，请基于你自己的知识回答，并注明这部分是你的知识而非参考信息。

参考信息:
{context_text}

用户问题: {query_text}"""
            
            messages = [
                {"role": "system", "content": "你是尊敬的马斯陶哥哥为乐乐独家打造的大模型 lele1.0，作为一个RAG教学项目，用于乐乐学习之用。你需要用温柔活泼的语气回答用户的问题。你将根据提供的参考信息回答问题。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用LLM获取流式回答
            self.llm_service.get_streaming_completion(messages, callback)
            
            return {
                "contexts": contexts,
                "has_context": True
            }