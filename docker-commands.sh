#!/bin/bash
# 🐳 Szybkie polecenia Docker Compose dla Image Stand

set -e

# Kolory dla outputu
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Image Stand - Docker Compose Commands${NC}\n"

# Funkcja pomocnicza
show_help() {
    echo "Użycie: ./docker-commands.sh [komenda]"
    echo ""
    echo "Dostępne komendy:"
    echo "  start       - Uruchom aplikację (build + up)"
    echo "  stop        - Zatrzymaj aplikację"
    echo "  restart     - Restart aplikacji"
    echo "  logs        - Pokaż logi (wszystkie serwisy)"
    echo "  logs-api    - Pokaż logi API"
    echo "  logs-frontend - Pokaż logi frontendu"
    echo "  status      - Status kontenerów"
    echo "  rebuild     - Przebuduj i uruchom"
    echo "  clean       - Zatrzymaj i usuń wszystko"
    echo "  test        - Test API health check"
    echo "  shell-api   - Otwórz shell w kontenerze API"
    echo "  shell-frontend - Otwórz shell w kontenerze frontendu"
    echo ""
}

# Sprawdź czy .env istnieje
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  Plik .env nie istnieje!${NC}"
        echo "Tworzenie z env.example..."
        if [ -f env.example ]; then
            cp env.example .env
            echo -e "${YELLOW}✏️  Edytuj .env i dodaj swoje klucze API!${NC}"
        else
            echo -e "${RED}❌ env.example nie istnieje!${NC}"
            exit 1
        fi
    fi
}

# Komendy
case "${1:-help}" in
    start)
        check_env
        echo -e "${GREEN}🚀 Uruchamianie aplikacji...${NC}"
        docker compose up --build -d
        echo -e "${GREEN}✅ Aplikacja uruchomiona!${NC}"
        echo ""
        echo "Frontend: http://localhost:8501"
        echo "API Docs: http://localhost:8000/docs"
        echo "API:      http://localhost:8000"
        ;;
    
    stop)
        echo -e "${YELLOW}🛑 Zatrzymywanie aplikacji...${NC}"
        docker compose down
        echo -e "${GREEN}✅ Aplikacja zatrzymana${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Restart aplikacji...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ Aplikacja zrestartowana${NC}"
        ;;
    
    logs)
        echo -e "${GREEN}📋 Logi wszystkich serwisów:${NC}"
        docker compose logs -f
        ;;
    
    logs-api)
        echo -e "${GREEN}📋 Logi API:${NC}"
        docker compose logs -f api
        ;;
    
    logs-frontend)
        echo -e "${GREEN}📋 Logi Frontendu:${NC}"
        docker compose logs -f frontend
        ;;
    
    status)
        echo -e "${GREEN}📊 Status kontenerów:${NC}"
        docker compose ps
        echo ""
        echo -e "${GREEN}💾 Użycie zasobów:${NC}"
        docker stats --no-stream
        ;;
    
    rebuild)
        check_env
        echo -e "${YELLOW}🔨 Przebudowywanie aplikacji...${NC}"
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        echo -e "${GREEN}✅ Aplikacja przebudowana i uruchomiona${NC}"
        ;;
    
    clean)
        echo -e "${RED}🧹 Czyszczenie (zatrzymaj i usuń wszystko)...${NC}"
        read -p "Czy na pewno? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose down -v
            echo -e "${GREEN}✅ Wyczyszczone${NC}"
        else
            echo "Anulowano"
        fi
        ;;
    
    test)
        echo -e "${GREEN}🧪 Test API health check...${NC}"
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo -e "${GREEN}✅ API działa!${NC}"
            curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/health
        else
            echo -e "${RED}❌ API nie odpowiada${NC}"
            echo "Sprawdź czy aplikacja jest uruchomiona: ./docker-commands.sh status"
        fi
        ;;
    
    shell-api)
        echo -e "${GREEN}🐚 Otwieranie shell w kontenerze API...${NC}"
        docker compose exec api /bin/bash || docker compose exec api /bin/sh
        ;;
    
    shell-frontend)
        echo -e "${GREEN}🐚 Otwieranie shell w kontenerze frontendu...${NC}"
        docker compose exec frontend /bin/bash || docker compose exec frontend /bin/sh
        ;;
    
    help|*)
        show_help
        ;;
esac


