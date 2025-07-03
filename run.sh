#!/bin/bash

echo "🎓 Running Student Feedback System (Backend Only)..."

# Check if virtual environment exists
if [ ! -d "feedback_system_env" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source feedback_system_env/bin/activate

# Check if required files exist
if [ ! -f "feedback_system.py" ]; then
    echo "❌ feedback_system.py not found."
    exit 1
fi

if [ ! -f "demo.py" ]; then
    echo "❌ demo.py not found."
    exit 1
fi

# Run backend script
echo "🚀 Running feedback analysis demo..."
python demo.py
