#!/bin/bash

# Fashion Store Application Manager
# A unified script to manage the Fashion Store application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application configuration
APP_NAME="fashion_store"
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"
ENV_FILE=".env"

# Helper functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Fashion Store Application Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found. Creating default .env file..."
        cat > "$ENV_FILE" << EOF
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# MongoDB Configuration
MONGO_URI=mongodb://admin:password123@mongo:27017/ecommerce_db

# Application Configuration
HOST=0.0.0.0
PORT=6600

# ML Configuration
MODELS_DIR=models
DATA_DIR=data

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs
EOF
        print_success "Default .env file created"
    fi
}

# Start application
start_app() {
    print_header
    print_info "Starting Fashion Store Application..."
    
    check_docker
    check_env
    
    # Check if containers are already running
    if docker-compose ps | grep -q "Up"; then
        print_warning "Application is already running. Use 'restart' to restart it."
        return 0
    fi
    
    # Start the application
    print_info "Building and starting containers..."
    docker-compose up --build -d
    
    # Wait for application to be ready
    print_info "Waiting for application to be ready..."
    sleep 10
    
    # Check if application is healthy
    if curl -f http://localhost:6600/ > /dev/null 2>&1; then
        print_success "Application started successfully!"
        print_info "🌐 Application is available at: http://localhost:6600"
        print_info "📊 MongoDB is available at: mongodb://admin:password123@localhost:27017/ecommerce_db"
    else
        print_error "Application failed to start. Check logs with: ./manage-app.sh logs"
        exit 1
    fi
}

# Start in development mode
start_dev() {
    print_header
    print_info "Starting Fashion Store Application in Development Mode..."
    
    check_docker
    check_env
    
    # Check if containers are already running
    if docker-compose -f "$DEV_COMPOSE_FILE" ps | grep -q "Up"; then
        print_warning "Application is already running in development mode. Use 'restart' to restart it."
        return 0
    fi
    
    # Start the application in development mode
    print_info "Building and starting containers in development mode..."
    docker-compose -f "$DEV_COMPOSE_FILE" up --build -d
    
    # Wait for application to be ready
    print_info "Waiting for application to be ready..."
    sleep 10
    
    # Check if application is healthy
    if curl -f http://localhost:6600/ > /dev/null 2>&1; then
        print_success "Application started successfully in development mode!"
        print_info "🌐 Application is available at: http://localhost:6600"
        print_info "📊 MongoDB is available at: mongodb://admin:password123@localhost:27017/ecommerce_db"
        print_info "🔄 File changes will be automatically synced"
    else
        print_error "Application failed to start. Check logs with: ./manage-app.sh logs"
        exit 1
    fi
}

# Restart application
restart_app() {
    print_header
    print_info "Restarting Fashion Store Application..."
    
    check_docker
    
    # Stop existing containers
    print_info "Stopping existing containers..."
    docker-compose down
    
    # Start the application
    start_app
}

# Stop application
stop_app() {
    print_header
    print_info "Stopping Fashion Store Application..."
    
    check_docker
    
    # Stop containers
    docker-compose down
    
    print_success "Application stopped successfully!"
}

# Delete application and data
delete_app() {
    print_header
    print_warning "This will delete the application and ALL data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deleting application and data..."
        
        check_docker
        
        # Stop and remove containers
        docker-compose down -v
        
        # Remove images
        docker rmi $(docker images -q "$APP_NAME*") 2>/dev/null || true
        
        # Remove volumes
        docker volume prune -f
        
        print_success "Application and data deleted successfully!"
    else
        print_info "Operation cancelled."
    fi
}

# Show application status
status_app() {
    print_header
    print_info "Fashion Store Application Status"
    echo
    
    check_docker
    
    # Show container status
    print_info "Container Status:"
    docker-compose ps
    
    echo
    
    # Show application health
    if curl -f http://localhost:6600/ > /dev/null 2>&1; then
        print_success "Application is running and healthy"
        print_info "🌐 Application: http://localhost:6600"
        print_info "📊 MongoDB: mongodb://admin:password123@localhost:27017/ecommerce_db"
    else
        print_error "Application is not responding"
    fi
}

# Show application logs
show_logs() {
    print_header
    print_info "Fashion Store Application Logs"
    echo
    
    check_docker
    
    # Show logs
    docker-compose logs -f
}

# Show application logs (last 100 lines)
show_logs_tail() {
    print_header
    print_info "Fashion Store Application Logs (Last 100 lines)"
    echo
    
    check_docker
    
    # Show last 100 lines of logs
    docker-compose logs --tail=100
}

# Run tests
run_tests() {
    print_header
    print_info "Running Fashion Store Application Tests"
    echo
    
    check_docker
    
    # Run tests inside the container
    print_info "Running tests..."
    docker-compose exec web python tests/test_app.py
    
    print_success "Tests completed!"
}

# Run migrations
run_migrations() {
    print_header
    print_info "Running Database Migrations"
    echo
    
    check_docker
    
    # Run migrations inside the container
    print_info "Running migrations..."
    docker-compose exec web python migrate/run_migrations.py
    
    print_success "Migrations completed!"
}

# Show help
show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start       Start the application"
    echo "  start-dev   Start the application in development mode (with file sync)"
    echo "  restart     Restart the application"
    echo "  stop        Stop the application"
    echo "  delete      Delete the application and all data"
    echo "  status      Show application status"
    echo "  logs        Show application logs (follow mode)"
    echo "  logs-tail   Show last 100 lines of logs"
    echo "  test        Run application tests"
    echo "  migrate     Run database migrations"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start        # Start the application"
    echo "  $0 start-dev    # Start in development mode"
    echo "  $0 restart      # Restart the application"
    echo "  $0 logs         # View logs"
    echo "  $0 test         # Run tests"
    echo
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            start_app
            ;;
        start-dev)
            start_dev
            ;;
        restart)
            restart_app
            ;;
        stop)
            stop_app
            ;;
        delete)
            delete_app
            ;;
        status)
            status_app
            ;;
        logs)
            show_logs
            ;;
        logs-tail)
            show_logs_tail
            ;;
        test)
            run_tests
            ;;
        migrate)
            run_migrations
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
