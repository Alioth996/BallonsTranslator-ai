# PaddleOCR和OpenCV依赖修复说明

## 问题描述

在运行BallonsTranslator时，可能会遇到以下两个问题：

1. **PaddleOCR导入错误**：
   ```
   Error: Can not import paddle core while this file exists: E:\Program Files\BallonsTranslator\ballontrans_pylibs_win\lib\site-packages\paddle\base\libpaddle.pyd 
   [WARNING] ocr_paddle:<module>:12 - PaddleOCR is not installed, so the module will not be initialized.
   ```

2. **OpenCV依赖冲突**：
   ```
   ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
   paddleocr 2.7.0.3 requires opencv-python<=4.6.0.66, but you have opencv-python 4.11.0.86 which is incompatible.
   ```

## 解决方法

### 步骤1：修复PaddleOCR安装问题

1. 运行`fix_paddle.bat`批处理文件：
   ```
   fix_paddle.bat
   ```

2. 该脚本会自动执行以下操作：
   - 尝试快速修复libpaddle.pyd文件路径问题
   - 如果快速修复失败，会尝试完整修复（卸载并重新安装PaddlePaddle和PaddleOCR）
   - 如果完整修复也失败，会运行install_paddle.bat脚本

### 步骤2：修复OpenCV依赖冲突

1. 运行`fix_opencv.bat`批处理文件：
   ```
   fix_opencv.bat
   ```

2. 该脚本会自动执行以下操作：
   - 卸载当前的OpenCV版本
   - 安装兼容的NumPy版本(1.23.5)
   - 安装兼容的OpenCV版本(4.6.0.66)
   - 验证PaddleOCR是否可以正常导入

## 手动解决方法

如果自动修复脚本失败，可以尝试以下手动步骤：

### 修复PaddleOCR问题：

1. 卸载现有的PaddlePaddle和PaddleOCR：
   ```
   ballontrans_pylibs_win\python.exe -m pip uninstall -y paddlepaddle paddleocr
   ```

2. 安装PaddlePaddle 2.5.2：
   ```
   ballontrans_pylibs_win\python.exe -m pip install paddlepaddle==2.5.2 --no-cache-dir
   ```

3. 如果libpaddle.pyd文件路径错误，手动复制：
   - 查找libpaddle.pyd文件（通常在paddle/fluid/目录下）
   - 确保paddle/base/目录存在
   - 将libpaddle.pyd复制到paddle/base/目录下

4. 安装PaddleOCR 2.7.0.3：
   ```
   ballontrans_pylibs_win\python.exe -m pip install paddleocr==2.7.0.3
   ```

### 修复OpenCV依赖冲突：

1. 安装兼容的NumPy版本：
   ```
   ballontrans_pylibs_win\python.exe -m pip install numpy==1.23.5 --force-reinstall
   ```

2. 安装兼容的OpenCV版本：
   ```
   ballontrans_pylibs_win\python.exe -m pip install opencv-python==4.6.0.66
   ```

## 验证安装

运行以下命令验证PaddleOCR和OpenCV是否正常工作：
```
ballontrans_pylibs_win\python.exe test_paddleocr_working.py
```

如果输出"测试成功！PaddleOCR可以正常工作。"，则表示问题已解决。

## 注意事项

- 确保有足够的磁盘空间（至少需要1GB）
- 安装过程可能需要几分钟时间，请耐心等待
- 如果遇到网络问题，可能需要使用代理或更换网络环境
- 修复完成后，请重启BallonsTranslator以使用PaddleOCR功能
