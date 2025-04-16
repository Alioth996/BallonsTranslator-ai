@echo off
cd /d "%~dp0"
echo 正在修复PaddleOCR问题...

:: 首先尝试快速修复
echo 尝试快速修复...
ballontrans_pylibs_win\python.exe quick_fix_paddle.py
if %ERRORLEVEL% EQU 0 (
    echo 快速修复成功！
    goto :end
)

:: 如果快速修复失败，尝试完整修复
echo 快速修复失败，尝试完整修复...
ballontrans_pylibs_win\python.exe fix_paddle_issue.py
if %ERRORLEVEL% EQU 0 (
    echo 完整修复成功！
    goto :end
)

:: 如果完整修复也失败，运行安装脚本
echo 完整修复失败，尝试重新安装PaddleOCR...
call install_paddle.bat

:end
echo.
echo 修复过程完成，请重启BallonsTranslator以使用PaddleOCR功能。
pause
