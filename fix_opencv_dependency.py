import subprocess
import sys
import os
import time

def run_command(cmd):
    """运行命令并返回输出"""
    print(f"执行命令: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore'), process.returncode

def main():
    print("开始修复OpenCV依赖冲突...")
    python_exe = os.path.join("ballontrans_pylibs_win", "python.exe")

    # 检查Python解释器
    if not os.path.exists(python_exe):
        print(f"错误: 找不到Python解释器 {python_exe}")
        return False

    # 检查当前numpy版本
    print("检查当前NumPy版本...")
    stdout, stderr, code = run_command(f'"{python_exe}" -c "import numpy; print(numpy.__version__)"')
    if code != 0:
        print(f"获取NumPy版本失败: {stderr}")
        return False

    numpy_version = stdout.strip()
    print(f"当前NumPy版本: {numpy_version}")

    # 检查当前opencv-python版本
    try:
        stdout, stderr, code = run_command(f'"{python_exe}" -c "import cv2; print(cv2.__version__)"')
        if code == 0:
            current_version = stdout.strip()
            print(f"当前OpenCV版本: {current_version}")
    except:
        print("无法获取当前OpenCV版本")

    # 首先卸载opencv-python
    print("卸载当前OpenCV版本...")
    run_command(f'"{python_exe}" -m pip uninstall -y opencv-python opencv-python-headless')

    # 安装兼容的numpy版本
    print("安装兼容的NumPy版本(1.23.5)...")
    stdout, stderr, code = run_command(f'"{python_exe}" -m pip install numpy==1.23.5 --force-reinstall')
    if code != 0:
        print(f"安装NumPy 1.23.5失败: {stderr}")
        # 继续尝试安装OpenCV

    # 安装兼容的opencv-python版本
    print("安装兼容的OpenCV版本(4.6.0.66)...")
    stdout, stderr, code = run_command(f'"{python_exe}" -m pip install opencv-python==4.6.0.66')
    if code != 0:
        print(f"安装OpenCV 4.6.0.66失败: {stderr}")
        # 尝试安装其他兼容版本
        print("尝试安装OpenCV 4.5.5.64...")
        stdout, stderr, code = run_command(f'"{python_exe}" -m pip install opencv-python==4.5.5.64')
        if code != 0:
            print(f"安装OpenCV 4.5.5.64失败: {stderr}")
            return False

    # 等待安装完成
    print("等待安装完成...")
    time.sleep(3)

    # 验证安装
    print("验证NumPy和OpenCV版本...")
    stdout, stderr, code = run_command(f'"{python_exe}" -c "import numpy; print(\'NumPy版本: \' + numpy.__version__)"')
    if code != 0:
        print(f"验证NumPy版本失败: {stderr}")
    else:
        print(stdout.strip())

    stdout, stderr, code = run_command(f'"{python_exe}" -c "import cv2; print(\'OpenCV版本: \' + cv2.__version__)"')
    if code != 0:
        print(f"验证OpenCV版本失败: {stderr}")
        return False
    else:
        print(stdout.strip())

    # 检查paddleocr是否可以正常导入
    print("验证PaddleOCR是否可以正常导入...")
    stdout, stderr, code = run_command(f'"{python_exe}" -c "from paddleocr import PaddleOCR; print(\'PaddleOCR导入成功\')"')
    if code != 0:
        print(f"PaddleOCR导入失败: {stderr}")
        return False

    print(stdout.strip())
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n修复完成！OpenCV依赖冲突已解决。")
    else:
        print("\n修复失败！请尝试以下步骤手动解决:\n1. pip install numpy==1.23.5\n2. pip install opencv-python==4.6.0.66")
