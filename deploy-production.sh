#!/bin/bash

# Production Deployment Script for Fashion Store
# Domain: https://fashionstore.wehelloworld.com/
# Uses: Docker + Nginx + Certbot for SSL

set -e

DOMAIN="fashionstore.wehelloworld.com"
EMAIL="baonguyen.work@gmail.com"  # Change this to your email
APP_PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Fashion Store Production Deploy${NC}"
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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use sudo)"
        exit 1
    fi
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        print_info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl start docker
        systemctl enable docker
        print_success "Docker installed"
    else
        print_success "Docker already installed"
    fi
}

# Install Docker Compose if not present
install_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_info "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed"
    else
        print_success "Docker Compose already installed"
    fi
}

# Install Nginx
install_nginx() {
    if ! command -v nginx &> /dev/null; then
        print_info "Installing Nginx..."
        apt update
        apt install -y nginx
        systemctl start nginx
        systemctl enable nginx
        print_success "Nginx installed"
    else
        print_success "Nginx already installed"
    fi
}

# Install Certbot
install_certbot() {
    if ! command -v certbot &> /dev/null; then
        print_info "Installing Certbot..."
        apt install -y certbot python3-certbot-nginx
        print_success "Certbot installed"
    else
        print_success "Certbot already installed"
    fi
}

# Create production Dockerfile
create_production_dockerfile() {
    print_info "Creating production Dockerfile..."
    cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

RUN python -m spacy download en_core_web_md

COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
COPY main.py .
COPY data/ ./data/
COPY models/ ./models/
COPY migrate/ ./migrate/
RUN mkdir -p logs

ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:8000", "--timeout", "120", "main:app"]
EOF
    print_success "Production Dockerfile created"
}

# Create production docker-compose
create_production_compose() {
    print_info "Creating production docker-compose.yml..."
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  mongo:
    image: mongo:7.0
    container_name: fashion_store_mongo
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: ecommerce_db
    volumes:
      - mongo_data:/data/db
      - ./src/config/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - fashion_store_network

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: fashion_store_web
    restart: unless-stopped
    environment:
      - MONGO_URI=mongodb://admin:password123@mongo:27017/ecommerce_db?authSource=admin
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=8000
    depends_on:
      - mongo
    volumes:
      - ./data:/app/data:ro
      - ./models:/app/models
      - ./.env:/app/.env:ro
    networks:
      - fashion_store_network

volumes:
  mongo_data:

networks:
  fashion_store_network:
    driver: bridge
EOF
    print_success "Production docker-compose.yml created"
}

# Create Nginx configuration
create_nginx_config() {
    print_info "Creating Nginx configuration..."
    cat > /etc/nginx/sites-available/fashionstore << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Enable the site
    ln -sf /etc/nginx/sites-available/fashionstore /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    nginx -t
    systemctl reload nginx
    print_success "Nginx configuration created"
}

# Setup SSL with Certbot
setup_ssl() {
    print_info "Setting up SSL certificate..."
    
    # Stop nginx temporarily for certbot
    systemctl stop nginx
    
    # Get SSL certificate
    certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Update nginx config for HTTPS
    cat > /etc/nginx/sites-available/fashionstore << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Start nginx
    systemctl start nginx
    systemctl reload nginx
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    print_success "SSL certificate configured"
}

# Extract static assets
extract_assets() {
    if [ -f "static.zip" ]; then
        print_info "Extracting static assets..."
        unzip -o static.zip -d .
        print_success "Static assets extracted"
    else
        print_warning "static.zip not found - images may not display"
    fi
}

# Deploy application
deploy_app() {
    print_info "Deploying application..."
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Build and start
    docker-compose -f docker-compose.prod.yml up --build -d
    
    # Wait for services
    sleep 30
    
    print_success "Application deployed"
}

# Restore database
restore_database() {
    print_info "Restoring database..."
    
    # Copy dump to container
    docker cp migrate/mongodb_dump fashion_store_mongo:/tmp/
    
    # Install tools and restore
    docker exec -u root -i fashion_store_mongo bash -lc '
        apt-get update && apt-get install -y mongodb-database-tools
        mongorestore --host localhost:27017 --username admin --password password123 \
        --authenticationDatabase admin --db ecommerce_db --drop /tmp/mongodb_dump/ecommerce_db
    '
    
    print_success "Database restored"
}

# Sync images
sync_images() {
    print_info "Syncing images to container..."
    docker cp static/. fashion_store_web:/app/static
    print_success "Images synced"
}

# Verify deployment
verify_deployment() {
    print_info "Verifying deployment..."
    
    # Check if app is responding
    if curl -f http://localhost:$APP_PORT/ > /dev/null 2>&1; then
        print_success "Application is running"
    else
        print_error "Application is not responding"
        return 1
    fi
    
    # Check HTTPS
    if curl -f https://$DOMAIN/ > /dev/null 2>&1; then
        print_success "HTTPS is working"
    else
        print_warning "HTTPS may not be working yet (DNS propagation)"
    fi
}

# Main deployment function
main() {
    print_header
    print_info "Deploying Fashion Store to https://$DOMAIN"
    echo
    
    # Update email if needed
    if [ "$EMAIL" = "your-email@example.com" ]; then
        print_warning "Please update EMAIL variable in this script"
        read -p "Enter your email for SSL certificate: " EMAIL
    fi
    
    check_root
    install_docker
    install_docker_compose
    install_nginx
    install_certbot
    create_production_dockerfile
    create_production_compose
    extract_assets
    create_nginx_config
    setup_ssl
    deploy_app
    restore_database
    sync_images
    verify_deployment
    
    print_success "Deployment complete!"
    echo
    print_info "Your app is available at: https://$DOMAIN"
    print_info "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
    print_info "To restart: docker-compose -f docker-compose.prod.yml restart"
    print_info "To stop: docker-compose -f docker-compose.prod.yml down"
}

# Run main function
main "$@"
