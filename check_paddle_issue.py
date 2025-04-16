import os
import sys
import importlib.util
import shutil

def check_file_exists(file_path):
    """检查文件是否存在"""
    exists = os.path.exists(file_path)
    print(f"检查文件 {file_path}: {'存在' if exists else '不存在'}")
    return exists

def check_module_importable(module_name):
    """检查模块是否可导入"""
    try:
        importlib.import_module(module_name)
        print(f"模块 {module_name} 可以成功导入")
        return True
    except Exception as e:
        print(f"导入模块 {module_name} 失败: {e}")
        return False

def main():
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")
    
    # 检查paddle核心文件
    paddle_pyd = os.path.join("ballontrans_pylibs_win", "lib", "site-packages", "paddle", "base", "libpaddle.pyd")
    check_file_exists(paddle_pyd)
    
    # 检查paddle和paddleocr模块
    check_module_importable("paddle")
    check_module_importable("paddleocr")
    
    # 检查依赖库
    dependencies = ["numpy", "shapely", "pyclipper", "imgaug", "lmdb", "tqdm", "visualdl", "rapidfuzz"]
    for dep in dependencies:
        check_module_importable(dep)

if __name__ == "__main__":
    main()
