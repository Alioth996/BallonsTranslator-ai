import os
import sys
import shutil
import importlib.util
import subprocess

def run_command(cmd):
    """运行命令并返回输出"""
    print(f"执行命令: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore'), process.returncode

def check_paddle_installation():
    """检查paddle安装状态"""
    try:
        import paddle
        print(f"PaddlePaddle已安装，版本: {paddle.__version__}")
        return True
    except Exception as e:
        print(f"PaddlePaddle导入失败: {e}")
        return False

def main():
    print("开始修复PaddlePaddle安装问题...")
    python_exe = os.path.join("ballontrans_pylibs_win", "python.exe")
    
    # 检查Python解释器
    if not os.path.exists(python_exe):
        print(f"错误: 找不到Python解释器 {python_exe}")
        return
    
    # 卸载现有的paddle安装
    print("卸载现有的PaddlePaddle和PaddleOCR...")
    run_command(f'"{python_exe}" -m pip uninstall -y paddlepaddle paddleocr')
    
    # 清理pip缓存
    print("清理pip缓存...")
    run_command(f'"{python_exe}" -m pip cache purge')
    
    # 安装paddlepaddle
    print("安装PaddlePaddle...")
    stdout, stderr, code = run_command(f'"{python_exe}" -m pip install paddlepaddle==2.5.2 --no-cache-dir')
    if code != 0:
        print(f"安装PaddlePaddle失败: {stderr}")
        return
    
    # 检查libpaddle.pyd文件
    paddle_dir = os.path.join("ballontrans_pylibs_win", "lib", "site-packages", "paddle")
    base_dir = os.path.join(paddle_dir, "base")
    libpaddle_path = os.path.join(base_dir, "libpaddle.pyd")
    
    if not os.path.exists(libpaddle_path):
        print(f"警告: 找不到 {libpaddle_path}")
        
        # 尝试查找libpaddle.pyd文件
        for root, dirs, files in os.walk(paddle_dir):
            for file in files:
                if file == "libpaddle.pyd":
                    found_path = os.path.join(root, file)
                    print(f"在 {found_path} 找到libpaddle.pyd")
                    
                    # 确保base目录存在
                    os.makedirs(base_dir, exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(found_path, libpaddle_path)
                    print(f"已将libpaddle.pyd复制到 {libpaddle_path}")
                    break
            else:
                continue
            break
    
    # 安装paddleocr及其依赖
    print("安装PaddleOCR依赖...")
    run_command(f'"{python_exe}" -m pip install numpy==1.24.4')
    run_command(f'"{python_exe}" -m pip install shapely pyclipper imgaug lmdb tqdm visualdl rapidfuzz')
    
    print("安装PaddleOCR...")
    stdout, stderr, code = run_command(f'"{python_exe}" -m pip install paddleocr==2.7.0.3')
    if code != 0:
        print(f"安装PaddleOCR失败: {stderr}")
        return
    
    # 验证安装
    print("验证安装...")
    if check_paddle_installation():
        print("PaddlePaddle修复成功！")
    else:
        print("PaddlePaddle修复失败，请尝试运行install_paddle.bat")

if __name__ == "__main__":
    main()
