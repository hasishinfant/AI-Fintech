#!/bin/bash

# Intelli-Credit Setup Script
# This script sets up the complete Intelli-Credit system

set -e  # Exit on error

echo "=================================="
echo "Intelli-Credit Setup Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Python is installed
check_python() {
    print_info "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_info "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    echo ""
    print_info "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        cp .env.example .env
        print_success ".env file created"
        print_info "Please update .env file with your configuration"
    fi
    
    # Initialize database
    print_info "Initializing database..."
    python -c "from app.db.database import init_db; init_db()"
    print_success "Database initialized"
    
    cd ..
}

# Setup frontend
setup_frontend() {
    echo ""
    print_info "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_info "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        cp .env.example .env
        print_success ".env file created"
    fi
    
    cd ..
}

# Setup AI pipeline
setup_ai_pipeline() {
    echo ""
    print_info "Setting up AI pipeline..."
    
    # Check if Tesseract is installed (for OCR)
    if command -v tesseract &> /dev/null; then
        TESSERACT_VERSION=$(tesseract --version | head -n 1)
        print_success "Tesseract found: $TESSERACT_VERSION"
    else
        print_info "Tesseract OCR not found. Installing..."
        
        # Detect OS and install Tesseract
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install tesseract
                print_success "Tesseract installed via Homebrew"
            else
                print_error "Homebrew not found. Please install Tesseract manually."
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr
            print_success "Tesseract installed via apt"
        else
            print_error "Unsupported OS. Please install Tesseract manually."
        fi
    fi
}

# Create sample data
create_sample_data() {
    echo ""
    print_info "Creating sample data..."
    
    # Sample data is already in data/ directory
    if [ -d "data" ]; then
        print_success "Sample data directory exists"
    else
        mkdir -p data
        print_success "Sample data directory created"
        print_info "Please add sample documents to data/ directory"
    fi
}

# Run tests
run_tests() {
    echo ""
    print_info "Running tests..."
    
    # Backend tests
    cd backend
    source venv/bin/activate
    pytest tests/ -v
    print_success "Backend tests passed"
    cd ..
    
    # Frontend tests
    cd frontend
    npm test -- --run
    print_success "Frontend tests passed"
    cd ..
}

# Start services
start_services() {
    echo ""
    print_info "Starting services..."
    
    # Start backend
    print_info "Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    print_success "Backend started (PID: $BACKEND_PID)"
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    print_info "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    print_success "Frontend started (PID: $FRONTEND_PID)"
    cd ..
    
    echo ""
    print_success "All services started successfully!"
    echo ""
    echo "=================================="
    echo "Access the application:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "=================================="
    echo ""
    echo "To stop services:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
}

# Main setup flow
main() {
    echo "Starting setup process..."
    echo ""
    
    # Check prerequisites
    check_python
    check_node
    
    # Setup components
    setup_backend
    setup_frontend
    setup_ai_pipeline
    create_sample_data
    
    # Ask if user wants to run tests
    read -p "Do you want to run tests? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    # Ask if user wants to start services
    read -p "Do you want to start services now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
    else
        echo ""
        print_success "Setup complete!"
        echo ""
        echo "To start services manually:"
        echo "  Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
        echo "  Frontend: cd frontend && npm run dev"
        echo ""
    fi
}

# Run main function
main
