@echo off
cd /d "%~dp0"
echo Starting to fix PaddleOCR and OpenCV issues...

echo.
echo Step 1: Fixing PaddleOCR installation
echo ===========================
ballontrans_pylibs_win\python.exe fix_paddle_issue.py

echo.
echo Step 2: Fixing OpenCV dependency conflict
echo ===========================
ballontrans_pylibs_win\python.exe fix_opencv_dependency.py

echo.
echo Step 3: Verifying installation
echo ===========================
ballontrans_pylibs_win\python.exe test_paddleocr_working.py

echo.
echo Fix process completed! Please restart BallonsTranslator to use PaddleOCR.
echo If you still have issues, please refer to paddle_opencv_fix_readme.md file.
pause
