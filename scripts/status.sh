#!/bin/bash

# Deriv Bot - Status Script
# Verifica o status dos serviços do projeto

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    local service_name=$2
    local url=$3
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_success "$service_name is running on port $port"
        if [ ! -z "$url" ]; then
            print_status "  URL: $url"
        fi
        return 0
    else
        print_error "$service_name is not running on port $port"
        return 1
    fi
}

# Function to check service health
check_health() {
    local url=$1
    local service_name=$2
    
    if curl -s "$url" >/dev/null 2>&1; then
        print_success "$service_name is responding"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Function to check Python virtual environment
check_python_env() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Python virtual environment not activated"
        return 1
    else
        print_success "Python virtual environment is active: $VIRTUAL_ENV"
        return 0
    fi
}

# Function to check Node.js dependencies
check_node_deps() {
    if [ -d "frontend/node_modules" ]; then
        print_success "Frontend dependencies are installed"
        return 0
    else
        print_error "Frontend dependencies are not installed"
        return 1
    fi
}

# Function to check backend dependencies
check_backend_deps() {
    if [ -f "backend/venv/lib/python*/site-packages/flask" ]; then
        print_success "Backend dependencies are installed"
        return 0
    else
        print_error "Backend dependencies are not installed"
        return 1
    fi
}

# Main status function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Deriv Bot - Status Check${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""

    local backend_ok=false
    local frontend_ok=false
    local deps_ok=true

    # Check dependencies
    print_status "Checking dependencies..."
    check_python_env || deps_ok=false
    check_node_deps || deps_ok=false
    check_backend_deps || deps_ok=false
    echo ""

    # Check services
    print_status "Checking services..."
    check_port 5001 "Backend API" "http://localhost:5001" && backend_ok=true
    check_health "http://localhost:5001/api/health" "Backend Health" || backend_ok=false
    
    # Check frontend (try both ports)
    if check_port 5173 "Frontend" "http://localhost:5173"; then
        frontend_ok=true
    elif check_port 5174 "Frontend" "http://localhost:5174"; then
        frontend_ok=true
    else
        frontend_ok=false
    fi
    echo ""

    # Summary
    print_status "Summary:"
    if [ "$backend_ok" = true ] && [ "$frontend_ok" = true ]; then
        print_success "✅ All services are running!"
        echo ""
        print_status "Access URLs:"
        print_status "  Frontend: http://localhost:5173 (or 5174)"
        print_status "  Backend API: http://localhost:5001"
        print_status "  Health Check: http://localhost:5001/api/health"
    else
        print_error "❌ Some services are not running"
        if [ "$backend_ok" = false ]; then
            print_error "  Backend is not running"
        fi
        if [ "$frontend_ok" = false ]; then
            print_error "  Frontend is not running"
        fi
        echo ""
        print_status "To start services, run: ./start.sh"
    fi

    if [ "$deps_ok" = false ]; then
        echo ""
        print_warning "⚠️  Some dependencies are missing"
        print_status "To install dependencies, run: npm run install:all"
    fi
}

# Run main function
main "$@"
