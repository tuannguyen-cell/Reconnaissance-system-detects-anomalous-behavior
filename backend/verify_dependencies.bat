@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ==========================================
echo Backend Dependency Verification
echo ==========================================

set "PYTHON_EXE="
set "PIP_EXE="

if exist "%~dp0..\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0..\venv\Scripts\python.exe"
    set "PIP_EXE=%~dp0..\venv\Scripts\pip.exe"
    echo Using virtualenv: venv [CUDA/GPU]
) else (
    if exist "%~dp0..\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"
        set "PIP_EXE=%~dp0..\.venv\Scripts\pip.exe"
        echo Using virtualenv: .venv [CPU]
    ) else (
        set "PYTHON_EXE=python"
        set "PIP_EXE=pip"
        echo Using system Python
    )
)

echo 1. Checking Python version...
"%PYTHON_EXE%" --version

echo 2. Checking pip version...
"%PIP_EXE%" --version

echo 3. Checking installed packages...
"%PIP_EXE%" list

echo 4. Running basic imports and hardware check...
"%PYTHON_EXE%" -c "import sys; import fastapi; import uvicorn; import pydantic; import sqlalchemy; import torch; import cv2; import numpy as np; from ultralytics import YOLO; print('All critical imports successful!'); print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

echo ==========================================
echo Verification Complete
echo ==========================================
