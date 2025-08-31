#!/bin/bash

# Deriv Bot - Stop Script
# Para todos os serviços do projeto

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

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        print_status "Stopping process on port $port (PID: $pids)"
        echo $pids | xargs kill -9 2>/dev/null || true
        return 0
    else
        print_warning "No process found on port $port"
        return 1
    fi
}

# Function to kill processes by name
kill_process() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    if [ ! -z "$pids" ]; then
        print_status "Stopping $process_name processes (PID: $pids)"
        echo $pids | xargs kill -9 2>/dev/null || true
        return 0
    else
        print_warning "No $process_name processes found"
        return 1
    fi
}

# Main stop function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Deriv Bot - Stop Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""

    print_status "Stopping Deriv Bot services..."

    # Kill processes on specific ports
    print_status "Checking for processes on known ports..."
    kill_port 5001  # Backend port
    kill_port 5173  # Frontend port
    kill_port 5174  # Alternative frontend port

    # Kill processes by name
    print_status "Checking for processes by name..."
    kill_process "python.*main.py"  # Backend Python process
    kill_process "vite"             # Frontend Vite process
    kill_process "node.*vite"       # Node.js Vite process

    # Kill concurrently processes
    print_status "Checking for concurrently processes..."
    kill_process "concurrently"

    print_success "All Deriv Bot services stopped!"
    echo ""
    print_status "You can now run './start.sh' to start the services again"
}

# Run main function
main "$@"
