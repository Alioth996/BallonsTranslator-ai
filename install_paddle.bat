@echo off
cd /d "%~dp0"
echo 正在安装PaddlePaddle和PaddleOCR...

:: 首先卸载可能存在的不完整安装
ballontrans_pylibs_win\python.exe -m pip uninstall -y paddlepaddle paddleocr

:: 清理pip缓存
ballontrans_pylibs_win\python.exe -m pip cache purge

:: 安装paddlepaddle
echo 正在安装paddlepaddle...
ballontrans_pylibs_win\python.exe -m pip install paddlepaddle==2.5.2 --no-cache-dir

:: 安装paddleocr及其依赖
echo 正在安装paddleocr及其依赖...
ballontrans_pylibs_win\python.exe -m pip install numpy==1.24.4
ballontrans_pylibs_win\python.exe -m pip install shapely pyclipper imgaug lmdb tqdm visualdl rapidfuzz
ballontrans_pylibs_win\python.exe -m pip install paddleocr==2.7.0.3

:: 验证安装
echo 验证安装...
ballontrans_pylibs_win\python.exe -c "import paddle; print('PaddlePaddle版本:', paddle.__version__); import paddleocr; print('PaddleOCR安装成功')"

echo.
echo 安装完成！请重启BallonsTranslator以使用PaddleOCR功能。
pause
