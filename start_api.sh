#!/bin/bash
#
# Quick start script for the Trading System API
#
# Usage:
#   ./start_api.sh              # Development mode with auto-reload
#   ./start_api.sh --prod       # Production mode with 4 workers
#   ./start_api.sh --test       # Test mode (runs tests first)
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Multi-Agent Trading System API${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi
echo -e "${GREEN}✓ Found .env file${NC}"

# Check if dependencies are installed
echo -e "\n${BLUE}Checking dependencies...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Dependencies not installed${NC}"
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Parse arguments
MODE="dev"
RUN_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            MODE="prod"
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prod, --production  Run in production mode (4 workers)"
            echo "  --test                Run tests before starting"
            echo "  --help, -h            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    echo -e "\n${BLUE}Running tests...${NC}"
    python3 test_search_system.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Tests failed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Tests passed${NC}"
fi

# Start API server
echo -e "\n${BLUE}Starting API server...${NC}"
echo ""

if [ "$MODE" = "prod" ]; then
    echo -e "${GREEN}Mode: Production (4 workers)${NC}"
    echo -e "${GREEN}URL:  http://0.0.0.0:8000${NC}"
    echo -e "${GREEN}Docs: http://0.0.0.0:8000/docs${NC}"
    echo ""
    cd dashboard/backend
    uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo -e "${GREEN}Mode: Development (auto-reload)${NC}"
    echo -e "${GREEN}URL:  http://localhost:8000${NC}"
    echo -e "${GREEN}Docs: http://localhost:8000/docs${NC}"
    echo ""
    cd dashboard/backend
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
fi
