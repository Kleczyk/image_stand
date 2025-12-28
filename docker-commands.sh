#!/bin/bash
# 🐳 Quick Docker Compose commands for Image Stand

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Image Stand - Docker Compose Commands${NC}\n"

# Helper function
show_help() {
    echo "Usage: ./docker-commands.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  start       - Start application (build + up)"
    echo "  stop        - Stop application"
    echo "  restart     - Restart application"
    echo "  logs        - Show logs (all services)"
    echo "  logs-api    - Show API logs"
    echo "  logs-frontend - Show frontend logs"
    echo "  status      - Container status"
    echo "  rebuild     - Rebuild and start"
    echo "  clean       - Stop and remove everything"
    echo "  Test        - Test API health check"
    echo "  shell-api   - Open shell in API container"
    echo "  shell-frontend - Open shell in frontend container"
    echo ""
}

# Check if .env exists
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file does not exist!${NC}"
        echo "Creating from env.example..."
        if [ -f env.example ]; then
            cp env.example .env
            echo -e "${YELLOW}✏️  Edit .env and add your API keys!${NC}"
        else
            echo -e "${RED}❌ env.example does not exist!${NC}"
            exit 1
        fi
    fi
}

# Komendy
case "${1:-help}" in
    start)
        check_env
        echo -e "${GREEN}🚀 Starting application...${NC}"
        docker compose up --build -d
        echo -e "${GREEN}✅ Application started!${NC}"
        echo ""
        echo "Frontend: http://localhost:8501"
        echo "API Docs: http://localhost:8000/docs"
        echo "API:      http://localhost:8000"
        ;;
    
    stop)
        echo -e "${YELLOW}🛑 Stopping application...${NC}"
        docker compose down
        echo -e "${GREEN}✅ Application stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Restarting application...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ Application restarted${NC}"
        ;;
    
    logs)
        echo -e "${GREEN}📋 Logs from all services:${NC}"
        docker compose logs -f
        ;;
    
    logs-api)
        echo -e "${GREEN}📋 API logs:${NC}"
        docker compose logs -f api
        ;;
    
    logs-frontend)
        echo -e "${GREEN}📋 Frontend logs:${NC}"
        docker compose logs -f frontend
        ;;
    
    status)
        echo -e "${GREEN}📊 Container status:${NC}"
        docker compose ps
        echo ""
        echo -e "${GREEN}💾 Resource usage:${NC}"
        docker stats --no-stream
        ;;
    
    rebuild)
        check_env
        echo -e "${YELLOW}🔨 Rebuilding application...${NC}"
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        echo -e "${GREEN}✅ Application rebuilt and started${NC}"
        ;;
    
    clean)
        echo -e "${RED}🧹 Cleaning (stop and remove everything)...${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose down -v
            echo -e "${GREEN}✅ Cleaned${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    
    Test)
        echo -e "${GREEN}🧪 Testing API health check...${NC}"
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo -e "${GREEN}✅ API is working!${NC}"
            curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/health
        else
            echo -e "${RED}❌ API is not responding${NC}"
            echo "Check if application is running: ./docker-commands.sh status"
        fi
        ;;
    
    shell-api)
        echo -e "${GREEN}🐚 Opening shell in API container...${NC}"
        docker compose exec api /bin/bash || docker compose exec api /bin/sh
        ;;
    
    shell-frontend)
        echo -e "${GREEN}🐚 Opening shell in frontend container...${NC}"
        docker compose exec frontend /bin/bash || docker compose exec frontend /bin/sh
        ;;
    
    help|*)
        show_help
        ;;
esac


