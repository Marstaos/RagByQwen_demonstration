import os
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL_NAME

class LLMService:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = BASE_URL
        self.model = MODEL_NAME
        self.client = None
        
        # 如果API Key已配置，则初始化客户端
        if self.api_key:
            self._init_client()
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        except Exception as e:
            print(f"初始化客户端失败: {e}")
            self.client = None
    
    def update_api_key(self, new_api_key):
        """更新API Key并重新初始化客户端"""
        self.api_key = new_api_key
        self._init_client()
    
    def get_completion(self, messages):
        """调用大模型获取回复"""
        try:
            # 检查客户端是否已初始化
            if not self.client:
                return {
                    "success": False,
                    "error": "API Key未配置，请先设置API Key"
                }
                
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return {
                "success": True, 
                "content": completion.choices[0].message.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_streaming_completion(self, messages, callback):
        """流式调用大模型获取回复
        
        Args:
            messages: 对话消息列表
            callback: 每次收到流式内容时的回调函数，接收参数(content_delta, is_done)
        """
        try:
            # 检查客户端是否已初始化
            if not self.client:
                callback("API Key未配置，请先设置API Key", True)
                return False
                
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            # 处理流式响应
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_delta = chunk.choices[0].delta.content
                    callback(content_delta, False)
            
            # 流式输出完成
            callback("", True)
            return True
            
        except Exception as e:
            callback(f"错误: {str(e)}", True)