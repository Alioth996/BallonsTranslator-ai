import os
import sys

def main():
    print("测试PaddleOCR是否正常工作...")
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")
    
    try:
        import paddle
        print(f"PaddlePaddle版本: {paddle.__version__}")
        print(f"PaddlePaddle路径: {paddle.__file__}")
        
        # 检查libpaddle.pyd文件
        base_dir = os.path.join(os.path.dirname(paddle.__file__), "base")
        libpaddle_path = os.path.join(base_dir, "libpaddle.pyd")
        print(f"libpaddle.pyd存在: {os.path.exists(libpaddle_path)}")
        
        # 导入paddleocr
        from paddleocr import PaddleOCR
        print("PaddleOCR导入成功")
        
        # 尝试创建PaddleOCR实例
        print("尝试创建PaddleOCR实例...")
        ocr = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False)
        print("PaddleOCR实例创建成功")
        
        print("\n测试成功！PaddleOCR可以正常工作。")
        return True
    except Exception as e:
        print(f"\n测试失败: {e}")
        return False

if __name__ == "__main__":
    main()
