import sys
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaddleTest")

# 打印 Python 路径
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")

# 检查 PaddlePaddle 是否已安装
try:
    import paddle
    logger.info(f"PaddlePaddle version: {paddle.__version__}")
    logger.info(f"PaddlePaddle path: {paddle.__file__}")
except ImportError as e:
    logger.error(f"Failed to import PaddlePaddle: {e}")

# 检查 PaddleOCR 是否已安装
try:
    from paddleocr import PaddleOCR
    logger.info("PaddleOCR imported successfully")
    logger.info(f"PaddleOCR path: {PaddleOCR.__module__}")
except ImportError as e:
    logger.error(f"Failed to import PaddleOCR: {e}")

# 检查 PaddleOCR 的依赖项
dependencies = [
    "numpy", "opencv-python", "pyclipper", "shapely", 
    "imgaug", "lmdb", "tqdm", "visualdl", "rapidfuzz"
]

for dep in dependencies:
    try:
        module = __import__(dep.replace("-", "_"))
        logger.info(f"{dep} version: {getattr(module, '__version__', 'unknown')}")
    except ImportError as e:
        logger.error(f"Failed to import {dep}: {e}")

# 尝试创建 PaddleOCR 实例
try:
    ocr = PaddleOCR(use_angle_cls=False, lang="en")
    logger.info("PaddleOCR instance created successfully")
except Exception as e:
    logger.error(f"Failed to create PaddleOCR instance: {e}")
