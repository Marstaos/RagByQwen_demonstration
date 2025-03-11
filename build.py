import os
import sys
import shutil
import subprocess
import PyInstaller.__main__

def build_executable():
    """
    使用 PyInstaller 打包应用程序为单个可执行文件
    """
    print("开始打包应用程序...")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建临时目录用于存放打包过程中的文件
    build_dir = os.path.join(current_dir, "build_temp")
    dist_dir = os.path.join(current_dir, "dist")
    
    # 清理旧的构建文件
    for dir_path in [build_dir, dist_dir]:
        if os.path.exists(dir_path):
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    # 确保模型目录存在
    model_dir = os.path.join(current_dir, "models")
    if not os.path.exists(model_dir) or not os.listdir(model_dir):
        print("警告: 模型目录为空，请先运行 download_models.py 下载模型")
        download_models = input("是否现在下载模型? (y/n): ")
        if download_models.lower() == 'y':
            print("正在下载模型...")
            subprocess.run([sys.executable, os.path.join(current_dir, "download_models.py")])
        else:
            print("请先下载模型后再打包")
            return
    
    # 创建一个空的知识库目录，确保应用程序启动时有一个可用的知识库目录
    kb_dir = os.path.join(current_dir, "knowledge_base")
    os.makedirs(kb_dir, exist_ok=True)
    
    # 创建一个空的向量存储目录
    vector_dir = os.path.join(current_dir, "vector_store")
    os.makedirs(vector_dir, exist_ok=True)
    
    # 创建一个运行时配置文件，用于存储路径信息
    runtime_config = os.path.join(current_dir, "runtime_config.py")
    with open(runtime_config, "w", encoding="utf-8") as f:
        f.write("""
# 此文件由打包脚本自动生成，用于在运行时确定资源路径
import os
import sys

def get_resource_path(relative_path):
    \"\"\"获取资源的绝对路径，适用于开发环境和打包后的环境\"\"\"
    # 判断是否在打包环境中运行
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用程序，则使用sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # 如果是开发环境，则使用当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)
""")
    
    # 定义需要包含的数据文件
    datas = [
        (model_dir, "models"),
        (kb_dir, "knowledge_base"),
        (vector_dir, "vector_store"),
        (runtime_config, "."),  # 添加运行时配置文件
    ]
    
    # 将数据文件转换为 PyInstaller 格式
    datas_str = []
    for src, dst in datas:
        datas_str.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # 定义 PyInstaller 命令行参数
    pyinstaller_args = [
        "main.py",  # 主脚本
        "--name=乐乐的RAG学习助手",  # 可执行文件名称
        "--onedir",  # 创建一个目录而不是单个文件，以便包含大型模型
        "--windowed",  # 不显示控制台窗口
        "--icon=assets/icon.ico" if os.path.exists(os.path.join(current_dir, "assets/icon.ico")) else "",  # 图标
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问确认
        "--hidden-import=runtime_config",  # 确保导入运行时配置
    ] + datas_str
    
    # 过滤掉空参数
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    # 运行 PyInstaller
    print("正在运行 PyInstaller...")
    print(f"命令行参数: {' '.join(pyinstaller_args)}")
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("\n打包完成!")
    print(f"可执行文件位于: {os.path.join(dist_dir, '乐乐的RAG学习助手')}")
    print("请将整个目录复制到目标计算机上运行。")

if __name__ == "__main__":
    build_executable()