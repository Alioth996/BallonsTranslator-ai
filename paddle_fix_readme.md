# PaddleOCR修复说明

## 问题描述

在运行BallonsTranslator时，可能会遇到以下错误：

```
Error: Can not import paddle core while this file exists: E:\Program Files\BallonsTranslator\ballontrans_pylibs_win\lib\site-packages\paddle\base\libpaddle.pyd 
[WARNING] ocr_paddle:<module>:12 - PaddleOCR is not installed, so the module will not be initialized.  
Install core it by following https://www.paddlepaddle.org.cn/en/install/quick?docurl  
and then run `pip install paddleocr` paddle依然警告未下载,请排查原因并解决
```

这个问题是由于PaddlePaddle安装不完整或文件路径错误导致的。

## 解决方法

### 方法1：运行修复脚本

1. 运行`fix_paddle_issue.py`脚本：
   ```
   ballontrans_pylibs_win\python.exe fix_paddle_issue.py
   ```

2. 脚本会自动执行以下操作：
   - 卸载现有的PaddlePaddle和PaddleOCR
   - 清理pip缓存
   - 重新安装PaddlePaddle 2.5.2
   - 修复libpaddle.pyd文件路径问题
   - 安装PaddleOCR 2.7.0.3及其依赖

3. 完成后重启BallonsTranslator

### 方法2：手动安装

1. 运行`install_paddle.bat`脚本：
   ```
   install_paddle.bat
   ```

2. 如果安装后仍有问题，请检查以下文件是否存在：
   ```
   ballontrans_pylibs_win\lib\site-packages\paddle\base\libpaddle.pyd
   ```

3. 如果该文件不存在，但在其他位置找到了libpaddle.pyd文件（如`paddle\fluid\libpaddle.pyd`），请手动复制到`paddle\base\`目录下。

## 验证安装

运行测试脚本验证PaddleOCR是否正常工作：
```
ballontrans_pylibs_win\python.exe test_paddleocr_working.py
```

如果输出"测试成功！PaddleOCR可以正常工作。"，则表示问题已解决。

## 注意事项

- 确保有足够的磁盘空间（至少需要1GB）
- 安装过程可能需要几分钟时间，请耐心等待
- 如果遇到网络问题，可能需要使用代理或更换网络环境
