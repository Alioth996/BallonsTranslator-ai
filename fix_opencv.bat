@echo off
cd /d "%~dp0"
echo 正在修复OpenCV依赖冲突...

ballontrans_pylibs_win\python.exe fix_opencv_dependency.py
if %ERRORLEVEL% EQU 0 (
    echo 修复成功！
) else (
    echo 修复失败，尝试手动安装兼容版本...
    ballontrans_pylibs_win\python.exe -m pip install opencv-python==4.6.0.66 --force-reinstall
)

echo.
echo 修复过程完成，请重启BallonsTranslator。
pause
