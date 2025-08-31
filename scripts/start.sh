#!/bin/bash

# Deriv Bot - Startup Script
# Inicia tanto o backend quanto o frontend simultaneamente

set -e  # Exit on any error

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
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use. Killing existing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to check Python virtual environment
check_python_env() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Python virtual environment not activated"
        if [ -d "$PROJECT_ROOT/backend/venv" ]; then
            print_status "Activating virtual environment..."
            source "$PROJECT_ROOT/backend/venv/bin/activate"
        else
            print_error "Virtual environment not found. Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
            exit 1
        fi
    else
        print_success "Python virtual environment is active: $VIRTUAL_ENV"
    fi
}

# Function to check Node.js dependencies
check_node_deps() {
    if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        print_warning "Frontend dependencies not installed"
        print_status "Installing frontend dependencies..."
        cd "$PROJECT_ROOT/frontend"
        npm install
        cd "$PROJECT_ROOT"
    fi
}

# Function to check backend dependencies
check_backend_deps() {
    if [ ! -f "$PROJECT_ROOT/backend/venv/lib/python*/site-packages/flask" ]; then
        print_warning "Backend dependencies not installed"
        print_status "Installing backend dependencies..."
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate
        pip install -r requirements.txt
        cd "$PROJECT_ROOT"
    fi
}

# Main startup function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Deriv Bot - Startup Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""

    # Get the project root directory
    PROJECT_ROOT=$(pwd)
    print_status "Project root: $PROJECT_ROOT"

    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/package.json" ] || [ ! -d "$PROJECT_ROOT/frontend" ] || [ ! -d "$PROJECT_ROOT/backend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi

    print_status "Starting Deriv Bot..."

    # Check and kill existing processes
    print_status "Checking for existing processes..."
    kill_port 5001  # Backend port
    kill_port 5173  # Frontend port
    kill_port 5174  # Alternative frontend port

    # Check dependencies
    print_status "Checking dependencies..."
    check_python_env
    check_node_deps
    check_backend_deps

    # Start services
    print_status "Starting services..."
    print_status "Backend will run on: http://localhost:5001"
    print_status "Frontend will run on: http://localhost:5173 (or 5174 if 5173 is busy)"
    echo ""
    
    # Start backend first
    print_status "Starting backend..."
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd "$PROJECT_ROOT"
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:5001/api/health >/dev/null 2>&1; then
            print_success "Backend is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Start frontend
    print_status "Starting frontend..."
    cd "$PROJECT_ROOT/frontend"
    npm run dev &
    FRONTEND_PID=$!
    cd "$PROJECT_ROOT"
    
    print_success "Services started!"
    print_status "Backend PID: $BACKEND_PID (http://localhost:5001)"
    print_status "Frontend PID: $FRONTEND_PID (http://localhost:5173)"
    echo ""
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for interrupt
    trap "print_status 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; print_success 'Services stopped'; exit" INT
    wait
}

# Run main function
main "$@"
