
# 此文件由打包脚本自动生成，用于在运行时确定资源路径
import os
import sys

def get_resource_path(relative_path):
    """获取资源的绝对路径，适用于开发环境和打包后的环境"""
    # 判断是否在打包环境中运行
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用程序，则使用sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # 如果是开发环境，则使用当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)
