#!/bin/bash
# Setup script for Instagram Reels Scraper

set -e

echo "🎬 Instagram Reels Scraper - Setup Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Create output directories
echo "📁 Creating output directories..."
mkdir -p ~/Downloads/instagram_reels/{metadata,videos,logs}
mkdir -p ~/Downloads/instagram_reels/cron_logs
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Test imports
echo "🧪 Testing imports..."
python3 -c "
import requests
import rich
import loguru
import schedule
print('✅ All imports successful')
"
echo ""

# Configuration
echo "⚙️ Configuration:"
echo "  REELS_OUTPUT_DIR: ~/Downloads/instagram_reels"
echo "  CRON_LOGS_DIR: ~/Downloads/instagram_reels/cron_logs"
echo ""

# Summary
echo -e "${GREEN}=========================================="
echo "✅ Setup completed successfully!"
echo "==========================================${NC}"
echo ""
echo "📖 Next steps:"
echo ""
echo "1. Run scraper (standalone):"
echo "   python reels_scraper.py --hashtag reels --max-reels 10"
echo ""
echo "2. Start cron job manager:"
echo "   python cron_manager.py --action start"
echo ""
echo "3. Test configuration:"
echo "   python cron_manager.py --action test"
echo ""
echo "4. View logs:"
echo "   tail -f ~/Downloads/instagram_reels/logs/*.log"
echo ""
