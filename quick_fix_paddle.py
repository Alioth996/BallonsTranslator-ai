import os
import shutil

def main():
    """快速修复PaddlePaddle的libpaddle.pyd文件路径问题"""
    print("开始修复PaddlePaddle文件路径问题...")
    
    # 定义路径
    paddle_dir = os.path.join("ballontrans_pylibs_win", "lib", "site-packages", "paddle")
    base_dir = os.path.join(paddle_dir, "base")
    libpaddle_path = os.path.join(base_dir, "libpaddle.pyd")
    
    # 检查目标文件是否存在
    if os.path.exists(libpaddle_path):
        print(f"libpaddle.pyd已存在于 {libpaddle_path}，无需修复")
        return True
    
    # 确保base目录存在
    os.makedirs(base_dir, exist_ok=True)
    
    # 可能的源文件位置
    possible_locations = [
        os.path.join(paddle_dir, "fluid", "libpaddle.pyd"),
        os.path.join(paddle_dir, "libs", "libpaddle.pyd"),
        os.path.join(paddle_dir, "libpaddle.pyd")
    ]
    
    # 查找并复制文件
    for src_path in possible_locations:
        if os.path.exists(src_path):
            print(f"在 {src_path} 找到libpaddle.pyd")
            shutil.copy2(src_path, libpaddle_path)
            print(f"已将libpaddle.pyd复制到 {libpaddle_path}")
            return True
    
    # 如果在预定义位置找不到，则搜索整个paddle目录
    print("在预定义位置未找到libpaddle.pyd，正在搜索整个paddle目录...")
    for root, dirs, files in os.walk(paddle_dir):
        for file in files:
            if file == "libpaddle.pyd":
                src_path = os.path.join(root, file)
                print(f"在 {src_path} 找到libpaddle.pyd")
                shutil.copy2(src_path, libpaddle_path)
                print(f"已将libpaddle.pyd复制到 {libpaddle_path}")
                return True
    
    print("未找到libpaddle.pyd文件，请先安装PaddlePaddle")
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n修复完成！请重启BallonsTranslator以使用PaddleOCR功能。")
    else:
        print("\n修复失败！请运行install_paddle.bat安装PaddlePaddle。")
