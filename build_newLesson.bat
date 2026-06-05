@echo off
setlocal
cd /d "%~dp0"
python build_newLesson.py
if errorlevel 1 (
  echo.
  echo 打包失败
  exit /b 1
)
echo.
echo 打包成功
pause
