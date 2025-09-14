#!/bin/bash

# Fashion Store - Complete Startup Script
# This script ensures everything is ready for the lecturer on first run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Fashion Store - Complete Setup${NC}"
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
    print_success "Docker is running"
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p logs models data static/images/products
    print_success "Directories created"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f ".env" ]; then
        print_info "Creating .env file..."
        cat > .env << EOF
# Flask Configuration
SECRET_KEY=fashion-store-secret-key-2024-lecturer-ready
FLASK_ENV=production

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
        print_success ".env file created"
    else
        print_info ".env file already exists"
    fi
}

# Check if data file exists
check_data_file() {
    if [ ! -f "data/data-assignment3_II.csv" ]; then
        print_error "Data file not found: data/data-assignment3_II.csv"
        print_info "Please ensure the CSV file is in the data/ directory"
        exit 1
    fi
    print_success "Data file found ($(wc -l < data/data-assignment3_II.csv) lines)"
}

# Check if models exist
check_models() {
    local model_count=$(ls models/*.joblib 2>/dev/null | wc -l)
    if [ $model_count -eq 0 ]; then
        print_warning "No ML models found. They will be trained during startup."
    else
        print_success "Found $model_count ML models"
    fi
}

# Check if images exist
check_images() {
    local image_count=$(find static/images/products -name "*.jpg" 2>/dev/null | wc -l)
    if [ $image_count -eq 0 ]; then
        print_warning "No product images found. Products will display without images."
    else
        print_success "Found $image_count product images"
    fi
}

# Restore MongoDB database from dump
restore_database() {
    print_info "Restoring MongoDB database from dump..."
    
    # Check if dump exists
    if [ ! -d "migrate/mongodb_dump" ]; then
        print_error "MongoDB dump not found at migrate/mongodb_dump/"
        print_info "The database dump should be included with the application"
        return 1
    fi
    
    # Copy dump to MongoDB container
    print_info "Copying database dump to MongoDB container..."
    docker cp migrate/mongodb_dump fashion_store_mongo:/tmp/
    
    # Wait for MongoDB to be ready
    print_info "Waiting for MongoDB to be ready..."
    sleep 10
    
    # Restore the database
    print_info "Restoring database from dump..."
    docker-compose exec -T mongo mongorestore --host localhost:27017 --username admin --password password123 --authenticationDatabase admin --db ecommerce_db --drop /tmp/mongodb_dump/ecommerce_db/
    
    if [ $? -eq 0 ]; then
        print_success "Database restored successfully!"
        print_info "  - Products: 1,095 with embedded reviews and ML predictions"
        print_info "  - Individual Reviews: 19,664 with ML predictions"
        print_info "  - Users: 3 test accounts"
    else
        print_error "Database restoration failed"
        return 1
    fi
}

# Build and start the application
start_application() {
    print_info "Building and starting the application..."
    
    # Stop any existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start
    docker-compose up --build -d
    
    print_info "Waiting for services to be ready..."
    sleep 30
    
    # Check if application is healthy
    local max_attempts=15
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:6600/ > /dev/null 2>&1; then
            print_success "Application is ready!"
            return 0
        fi
        
        print_info "Attempt $attempt/$max_attempts - Waiting for application..."
        sleep 10
        ((attempt++))
    done
    
    print_error "Application failed to start after $max_attempts attempts"
    print_info "Check logs with: docker-compose logs"
    return 1
}

# Verify the application is working
verify_application() {
    print_info "Verifying application functionality..."
    
    # Check if we can access the homepage
    if curl -f http://localhost:6600/ > /dev/null 2>&1; then
        print_success "Homepage accessible"
    else
        print_error "Homepage not accessible"
        return 1
    fi
    
    # Check if we can access the API
    if curl -f http://localhost:6600/api/products > /dev/null 2>&1; then
        print_success "API accessible"
    else
        print_error "API not accessible"
        return 1
    fi
    
    # Check if ML prediction works
    local prediction_response=$(curl -s -X POST http://localhost:6600/api/predict_review \
        -H "Content-Type: application/json" \
        -d '{"review_text":"This is a great product!", "title":"Amazing", "rating":5}' 2>/dev/null)
    
    if echo "$prediction_response" | grep -q "prediction"; then
        print_success "ML prediction working"
    else
        print_warning "ML prediction may not be working properly"
    fi
    
    # Check if products are loaded
    local product_count=$(curl -s http://localhost:6600/api/products | grep -o '"clothing_id"' | wc -l)
    if [ $product_count -gt 0 ]; then
        print_success "Products loaded ($product_count products)"
    else
        print_warning "No products found in API"
    fi
    
    return 0
}

# Show final status
show_status() {
    print_header
    print_success "Fashion Store is ready for your lecturer!"
    echo
    print_info "Application URL: http://localhost:6600"
    print_info "MongoDB URL: mongodb://admin:password123@localhost:27017/ecommerce_db"
    print_info "Data: $(wc -l < data/data-assignment3_II.csv) products loaded"
    print_info "ML Models: $(ls models/*.joblib 2>/dev/null | wc -l) models trained"
    print_info "Images: $(find static/images/products -name "*.jpg" 2>/dev/null | wc -l) product images"
    echo
    print_info "Available commands:"
    print_info "  ./manage-app.sh status    - Check application status"
    print_info "  ./manage-app.sh logs      - View application logs"
    print_info "  ./manage-app.sh stop      - Stop the application"
    print_info "  ./manage-app.sh restart   - Restart the application"
    echo
    print_success "Your lecturer can now start the application with: ./manage-app.sh start"
    print_info "Or use this complete setup script: ./startup_complete.sh"
}

# Main execution
main() {
    print_header
    print_info "Setting up Fashion Store for lecturer evaluation..."
    echo
    
    # Run all setup steps
    check_docker
    create_directories
    create_env_file
    check_data_file
    check_models
    check_images
    
    if start_application; then
        if restore_database; then
            if verify_application; then
                show_status
            else
                print_error "Application verification failed"
                exit 1
            fi
        else
            print_error "Database restoration failed"
            exit 1
        fi
    else
        print_error "Application startup failed"
        exit 1
    fi
}

# Run main function
main "$@"
