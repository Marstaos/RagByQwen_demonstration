import os
import sys
from ui.app_ui import AppUI

def setup_packaged_environment():
    """为打包环境设置必要的配置"""
    # 检查是否在打包环境中运行
    if getattr(sys, 'frozen', False):
        # 获取应用程序所在目录
        app_dir = os.path.dirname(sys.executable)
        
        # 设置工作目录为应用程序目录
        os.chdir(app_dir)
        
        # 创建必要的目录
        for dir_name in ["knowledge_base", "vector_store"]:
            dir_path = os.path.join(app_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"创建目录: {dir_path}")
        
        print(f"应用程序运行在打包环境中，工作目录: {app_dir}")
    else:
        print(f"应用程序运行在开发环境中，工作目录: {os.getcwd()}")

def main():
    # 设置环境
    setup_packaged_environment()
    
    # 启动UI
    app = AppUI()
    app.mainloop()

if __name__ == "__main__":
    main()