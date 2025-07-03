#!/bin/bash

echo "🎓 Setting up Student Feedback Generation System (Backend Only)"
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv feedback_system_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source feedback_system_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To run the backend logic:"
echo "1. Activate the virtual environment: source feedback_system_env/bin/activate"
echo "2. Run the script: python demo.py"
echo ""
echo "📊 The system includes:"
echo "• AI-powered feedback analysis"
echo "• Reward system (Bronze, Silver, Gold, Platinum)"
echo "• Educator dashboard and alerts"
echo "• Student performance reports"
