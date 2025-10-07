#!/bin/bash

echo "========================================="
echo "Multi-PC Device Manager Setup"
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (y/n): " create_venv
if [ "$create_venv" = "y" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
    source env/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and update:"
    echo "   - PC host IPs (PC1_HOST, PC2_HOST, PC3_HOST)"
    echo "   - Security tokens (PC*_TOKEN, AGENT_TOKEN)"
    echo ""
    read -p "Open .env for editing now? (y/n): " edit_env
    if [ "$edit_env" = "y" ]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p agents/scripts agents/old-scripts master
echo "✅ Directories created"

# Check for ADB/SDB
echo ""
echo "Checking for device tools..."
if command -v adb &> /dev/null; then
    echo "✅ ADB found: $(adb version | head -1)"
else
    echo "⚠️  ADB not found. Install Android SDK platform-tools"
fi

if command -v sdb &> /dev/null; then
    echo "✅ SDB found"
else
    echo "⚠️  SDB not found (only needed for Tizen devices)"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. On Master PC (this one):"
echo "   - Edit .env with agent PC IPs and tokens"
echo "   - Run: make list-all"
echo ""
echo "2. On Each Agent PC:"
echo "   - Copy project to agent PC"
echo "   - Edit .env with AGENT_TOKEN"
echo "   - Run: make agent"
echo ""
echo "3. Start Automation:"
echo "   - Run: make run-all"
echo ""
echo "Quick commands:"
echo "  make list-all          - List all devices"
echo "  make run-all           - Run automation"
echo "  make distribution      - Show app distribution"
echo ""