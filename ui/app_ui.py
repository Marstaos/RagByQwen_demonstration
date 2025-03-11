import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox  # 添加messagebox
import customtkinter as ctk
from modules.rag_engine import RAGEngine
from modules.document_loader import DocumentLoader
from modules.vector_store import VectorStore
from modules.llm_service import LLMService 
from config import KNOWLEDGE_BASE_DIR, API_KEY 
from datetime import datetime

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 设置主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # 初始化组件
        self.rag_engine = RAGEngine()
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()
        
        # 设置窗口
        self.title("通义千问Plus RAG助手")
        self.geometry("1000x700")  # 调整窗口大小
        
        # 定义消息样式
        self.message_styles = {
            "系统": {"bg": "#E8F5E9", "fg": "#2E7D32", "prefix": "🔧 "},
            "用户": {"bg": "#E3F2FD", "fg": "#1976D2", "prefix": "👤 "},
            "助手": {"bg": "#FFF3E0", "fg": "#F57C00", "prefix": "🤖 "},
            "知识库": {"bg": "#F3E5F5", "fg": "#7B1FA2", "prefix": "📚 "}
        }
        
        # 添加API Key配置状态
        self.api_key_configured = False
        
        # 创建UI组件
        self.create_widgets()
        
        # 检查API Key配置
        self.check_api_key()
    
    def create_widgets(self):
        # 创建两个主要框架
        left_frame = ctk.CTkFrame(self, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧知识库管理框架
        kb_label = ctk.CTkLabel(left_frame, text="知识库管理", font=("Arial", 16, "bold"))
        kb_label.pack(pady=(10, 20))
        
        # 添加文档按钮
        add_doc_btn = ctk.CTkButton(left_frame, text="添加文档", command=self.add_document)
        add_doc_btn.pack(pady=5, fill=tk.X, padx=20)
        
        # 清空知识库按钮
        clear_kb_btn = ctk.CTkButton(left_frame, text="清空知识库", command=self.clear_knowledge_base)
        clear_kb_btn.pack(pady=5, fill=tk.X, padx=20)
        
        # 文档列表标签
        docs_label = ctk.CTkLabel(left_frame, text="已加载文档:", font=("Arial", 14))
        docs_label.pack(pady=(20, 5), anchor="w", padx=20)
        
        # 文档列表区域
        self.docs_listbox = tk.Listbox(left_frame, bg="#F0F0F0", fg="#333333", selectbackground="#007BFF")
        self.docs_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.update_documents_list(show_message=False)  # 初始化时不显示消息
        
        # 右侧聊天区域
        chat_label = ctk.CTkLabel(right_frame, text="与通义千问Plus对话", font=("Arial", 16, "bold"))
        chat_label.pack(pady=(10, 20))
        
        # 聊天历史区域
        self.chat_history = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            bg="#FFFFFF",
            fg="#333333",
            font=("Arial", 11),
            padx=10,
            pady=10
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.chat_history.config(state=tk.DISABLED)
        
        # 美化输入区域
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.user_input = ctk.CTkTextbox(
            input_frame,
            height=80,
            font=("Arial", 12),
            border_width=2,
            border_color="#E0E0E0"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        send_button = ctk.CTkButton(
            input_frame,
            text="发送",
            width=100,
            font=("Arial", 12, "bold"),
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # 在左侧框架顶部添加API Key配置区域
        api_frame = ctk.CTkFrame(left_frame)
        api_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        api_label = ctk.CTkLabel(api_frame, text="API Key设置", font=("Arial", 14, "bold"))
        api_label.pack(pady=(10, 5))
        
        self.api_key_entry = ctk.CTkEntry(api_frame, show="*", placeholder_text="输入API Key")
        self.api_key_entry.pack(fill=tk.X, pady=(0, 5))
        
        api_button = ctk.CTkButton(api_frame, text="保存API Key", command=self.save_api_key)
        api_button.pack(fill=tk.X)
    
    def check_api_key(self):
        """检查API Key是否已配置"""
        if not API_KEY:
            self.add_message("系统", "⚠️ 请先配置API Key才能开始对话")
            self.api_key_configured = False
        else:
            self.api_key_configured = True
    
    def save_api_key(self):
        """保存API Key"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self.add_message("系统", "❌ API Key不能为空")
            return
            
        # 更新全局API Key
        global API_KEY
        API_KEY = api_key
        
        # 更新LLM服务的API Key
        self.rag_engine.llm_service.update_api_key(api_key)
        
        self.api_key_configured = True
        self.add_message("系统", "✅ API Key配置成功")
        self.api_key_entry.delete(0, tk.END)
    
    def send_message(self):
        """发送消息"""
        if not self.api_key_configured:
            self.add_message("系统", "⚠️ 请先配置API Key")
            return
            
        query = self.user_input.get("1.0", tk.END).strip()
        if not query:
            return
        
        # 清空输入框
        self.user_input.delete("1.0", tk.END)
        
        # 在聊天历史中显示用户消息
        self.add_message("你", query)
        
        # 在后台处理请求
        threading.Thread(target=self._process_query, args=(query,)).start()
    
    def _process_query(self, query):
        """在后台处理查询"""
        try:
            # 调用RAG引擎处理查询
            result = self.rag_engine.query(query)
            
            if result["has_context"]:
                # 显示检索到的上下文信息
                self.after(0, lambda: self.add_message("系统", "📚 检索到以下相关内容:"))
                
                # 显示每个检索到的上下文
                for i, context in enumerate(result["contexts"]):
                    # 限制长度以避免显示过多
                    preview = context[:200] + "..." if len(context) > 200 else context
                    self.after(0, lambda: self.add_message("知识库", f"[片段 {i+1}] {preview}"))
            else:
                self.after(0, lambda: self.add_message("系统", "⚠️ 未检索到相关知识，将使用模型的通用知识回答"))
            
            # 显示最终回答
            response = result["response"]
            if response["success"]:
                self.after(0, lambda: self.add_message("助手", response["content"]))
            else:
                self.after(0, lambda: self.add_message("系统", f"查询失败: {response['error']}"))
        except Exception as e:
            self.after(0, lambda: self.add_message("系统", f"处理查询时出错: {str(e)}"))

    def add_document(self):
        """添加文档到知识库"""
        file_path = filedialog.askopenfilename(
            title="选择文档",
            filetypes=[
                ("文本文件", "*.txt"),
                ("Markdown文件", "*.md"),
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            # 在后台处理文档
            self.add_message("系统", f"开始处理文档: {os.path.basename(file_path)}")
            threading.Thread(target=self._process_document, args=(file_path,)).start()

    def _process_document(self, file_path):
        """在后台处理文档"""
        try:
            # 加载文档
            text = self.document_loader.load_document(file_path)
            self.after(0, lambda: self.add_message("系统", f"文档加载成功，文本长度: {len(text)} 字符"))
            
            # 分割文本
            chunks = self.document_loader.split_text(text)
            self.after(0, lambda: self.add_message("系统", f"文本分割完成，共 {len(chunks)} 个片段"))
            
            # 添加到向量存储
            source_name = os.path.basename(file_path)
            success = self.vector_store.add_texts(chunks, source_name)
            
            if success:
                self.after(0, lambda: self.add_message("系统", f"✅ 文档 '{source_name}' 已成功添加到知识库"))
                # 更新文档列表，并显示消息
                self.after(0, lambda: self.update_documents_list(show_message=True))
            else:
                self.after(0, lambda: self.add_message("系统", f"❌ 文档 '{source_name}' 添加失败"))
                
        except Exception as e:
            self.after(0, lambda: self.add_message("系统", f"处理文档时出错: {str(e)}"))

    def clear_knowledge_base(self):
        """清空知识库"""
        confirm = tk.messagebox.askyesno("确认", "确定要清空知识库吗？此操作不可恢复。")
        if confirm:
            try:
                self.vector_store.clear()
                self.add_message("系统", "✅ 知识库已清空")
                # 更新文档列表，并显示消息
                self.update_documents_list(show_message=True)
            except Exception as e:
                self.add_message("系统", f"清空知识库时出错: {str(e)}")

    def update_documents_list(self, show_message=False):
        """更新已加载文档列表"""
        try:
            # 清空当前列表
            self.docs_listbox.delete(0, tk.END)
            
            # 如果向量存储为空，则显示提示信息
            if not self.vector_store.texts:
                self.docs_listbox.insert(tk.END, "暂无文档")
                return
                
            # 获取所有文档的来源信息
            sources = set()
            for text in self.vector_store.texts:
                if "\n\n" in text:
                    source = text.split("\n\n")[0].replace("来源: ", "")
                    sources.add(source)
            
            # 按字母顺序排序并显示
            for source in sorted(sources):
                self.docs_listbox.insert(tk.END, source)
                
            # 如果有文档且需要显示消息，显示数量
            if sources and show_message:
                self.add_message("系统", f"已加载 {len(sources)} 个文档")
        except Exception as e:
            if show_message:
                self.add_message("系统", f"更新文档列表时出错: {str(e)}")
            else:
                print(f"更新文档列表时出错: {str(e)}")

    def add_message(self, sender, message):
        """向聊天历史添加消息"""
        # 获取发送者的样式
        style = self.message_styles.get(sender, {"bg": "#F5F5F5", "fg": "#333333", "prefix": ""})
        
        # 启用编辑
        self.chat_history.config(state=tk.NORMAL)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # 添加发送者和消息
        sender_text = f"{style['prefix']}{sender}: "
        self.chat_history.insert(tk.END, sender_text, f"sender_{sender}")
        self.chat_history.insert(tk.END, f"{message}\n\n", f"message_{sender}")
        
        # 应用样式标签
        self.chat_history.tag_config("timestamp", foreground="#999999")
        self.chat_history.tag_config(f"sender_{sender}", foreground=style["fg"], font=("Arial", 11, "bold"))
        self.chat_history.tag_config(f"message_{sender}", foreground=style["fg"])
        
        # 滚动到底部
        self.chat_history.see(tk.END)
        
        # 禁用编辑
        self.chat_history.config(state=tk.DISABLED)