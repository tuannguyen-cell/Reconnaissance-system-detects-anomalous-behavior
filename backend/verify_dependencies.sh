#!/bin/bash

echo "=========================================="
echo "Backend Dependency Verification"
echo "=========================================="

cd backend

echo "1. Checking Python version..."
python --version

echo "2. Checking pip version..."
pip --version

echo "3. Checking for security vulnerabilities..."
pip install pip-audit
pip-audit

echo "4. Installing dependencies..."
pip install --upgrade -r requirements.txt

echo "5. Checking installed packages..."
pip list

echo "6. Running basic imports check..."
python -c "
import sys
try:
    import fastapi
    import uvicorn
    import pydantic
    import sqlalchemy
    import torch
    import cv2
    import numpy as np
    print('All critical imports successful!')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"

echo "=========================================="
echo "Verification Complete"
echo "=========================================="
