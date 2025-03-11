import PyInstaller.__main__
import os
import shutil
from config import MODEL_DIR

def build_exe():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建一个assets目录用于存放图标等资源
    assets_dir = os.path.join(current_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # 确保模型目录存在
    if not os.path.exists(MODEL_DIR) or len(os.listdir(MODEL_DIR)) == 0:
        print("警告: 模型目录为空，请先运行 download_models.py 下载模型!")
        return
    
    # 设置打包参数
    params = [
        'main.py',                 # 主程序入口
        '--name=通义千问Plus助手',  # 程序名称
        '--onefile',               # 打包成单个文件
        '--noconsole',             # 不显示控制台窗口
        f'--distpath={os.path.join(current_dir, "dist")}',  # 输出目录
        f'--workpath={os.path.join(current_dir, "build")}',  # 工作目录
        '--clean',                 # 清理临时文件
        '--add-data=knowledge_base;knowledge_base',  # 添加知识库目录
        '--add-data=vector_store;vector_store',      # 添加向量存储目录
        f'--add-data={MODEL_DIR};models',            # 添加模型目录
    ]
    
    # 运行PyInstaller
    PyInstaller.__main__.run(params)
    
    print("打包完成! 可执行文件位于 dist 目录.")

if __name__ == "__main__":
    build_exe()