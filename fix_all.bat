@echo off
cd /d "%~dp0"
echo 开始全面修复PaddleOCR和OpenCV问题...

echo.
echo 步骤1: 修复PaddleOCR安装问题
echo ===========================
call fix_paddle.bat

echo.
echo 步骤2: 修复OpenCV依赖冲突
echo ===========================
call fix_opencv.bat

echo.
echo 步骤3: 验证安装
echo ===========================
ballontrans_pylibs_win\python.exe test_paddleocr_working.py

echo.
echo 修复过程完成！请重启BallonsTranslator以使用PaddleOCR功能。
echo 如果仍有问题，请参考paddle_opencv_fix_readme.md文件中的手动解决方法。
pause
