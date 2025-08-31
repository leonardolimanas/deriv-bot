#!/bin/bash

# Deriv Bot - Installation Script
# Instala todas as dependências necessárias para o projeto

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        local version=$(python3 --version 2>&1 | cut -d' ' -f2)
        local major=$(echo $version | cut -d'.' -f1)
        local minor=$(echo $version | cut -d'.' -f2)
        
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            print_success "Python $version found"
            return 0
        else
            print_error "Python 3.8+ required, found $version"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check Node.js version
check_node() {
    if command_exists node; then
        local version=$(node --version 2>&1 | cut -d'v' -f2)
        local major=$(echo $version | cut -d'.' -f1)
        
        if [ "$major" -ge 16 ]; then
            print_success "Node.js $version found"
            return 0
        else
            print_error "Node.js 16+ required, found $version"
            return 1
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

# Function to check npm
check_npm() {
    if command_exists npm; then
        local version=$(npm --version 2>&1)
        print_success "npm $version found"
        return 0
    else
        print_error "npm not found"
        return 1
    fi
}

# Function to create Python virtual environment
create_python_env() {
    if [ ! -d "backend/venv" ]; then
        print_status "Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    print_success "Python dependencies installed"
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Node.js dependencies installed"
}

# Function to install root dependencies
install_root_deps() {
    print_status "Installing root dependencies..."
    npm install
    print_success "Root dependencies installed"
}

# Function to create .env file
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your configuration"
        else
            print_warning "No env.example found. Please create .env file manually"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Main installation function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Deriv Bot - Installation${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""

    # Check if we're in the right directory
    if [ ! -f "package.json" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi

    print_status "Starting installation..."

    # Check prerequisites
    print_status "Checking prerequisites..."
    check_python || exit 1
    check_node || exit 1
    check_npm || exit 1
    echo ""

    # Install dependencies
    print_status "Installing dependencies..."
    install_root_deps
    create_python_env
    install_python_deps
    install_node_deps
    echo ""

    # Create .env file
    create_env_file
    echo ""

    print_success "Installation completed successfully!"
    echo ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your configuration"
    print_status "2. Run './start.sh' to start the services"
    print_status "3. Access the application at http://localhost:5173"
    echo ""
    print_status "Configuration files:"
    print_status "  - .env: Environment variables"
    print_status "  - backend/utils/config.py: Default configuration"
    echo ""
    print_status "Useful commands:"
    print_status "  - ./start.sh: Start services"
    print_status "  - ./stop.sh: Stop services"
    print_status "  - ./status.sh: Check service status"
}

# Run main function
main "$@"
