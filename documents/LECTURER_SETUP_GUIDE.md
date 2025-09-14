# Fashion Store - Lecturer Setup Guide

## Quick Start (Recommended)

The easiest way to get the Fashion Store application running is to use the complete setup script:

```bash
./startup_complete.sh
```

This script will:
1. Check all prerequisites (Docker, data files, ML models)
2. Build and start the application
3. Restore the complete database with all data and ML predictions
4. Verify everything is working correctly

## Alternative Setup Methods

### Method 1: Using the Management Script

```bash
# Complete setup (recommended)
./manage-app.sh setup

# Or step by step:
./manage-app.sh start
./manage-app.sh restore-db
```

### Method 2: Manual Setup

```bash
# Start the application
docker-compose up --build -d

# Wait for services to be ready
sleep 30

# Restore the database
./manage-app.sh restore-db
```

## What's Included

The application comes with a complete dataset:

### Database Content
- **1,095 Products** with full details and images
- **19,664 Individual Reviews** with ML predictions
- **19,678 Embedded Reviews** in products with ML predictions
- **3 Test User Accounts** for testing authentication

### ML Features
- **3 Machine Learning Models**: Logistic Regression, Random Forest, SVM
- **Ensemble Predictions**: Majority voting with confidence scores
- **Real-time Analysis**: AI predicts review sentiment as users type
- **User Override**: Users can override AI predictions with explanations

### User Accounts
- **admin@fashionstore.com** / password123
- **testuser1@fashionstore.com** / password123
- **testuser2@fashionstore.com** / password123

## Application Features

### For Students (HD Level Requirements)
1. **Advanced Search**: Keyword normalization, fuzzy matching
2. **AI-Powered Reviews**: Real-time ML prediction with confidence scores
3. **User Override System**: Override AI predictions with explanations
4. **Comprehensive Filtering**: Category, rating, price, division filters
5. **Responsive Design**: Mobile-friendly Bootstrap interface
6. **User Authentication**: Registration, login, profile management

### Technical Features
- **Docker Containerization**: Easy deployment and isolation
- **MongoDB Database**: NoSQL with embedded documents
- **Flask Web Framework**: Python backend with RESTful API
- **Machine Learning**: Scikit-learn models with spaCy NLP
- **Real-time Updates**: JavaScript for dynamic interactions

## Access Points

- **Main Application**: http://localhost:6600
- **MongoDB**: mongodb://admin:password123@localhost:27017/ecommerce_db
- **Logs**: `./manage-app.sh logs`

## Management Commands

```bash
./manage-app.sh start        # Start the application
./manage-app.sh stop         # Stop the application
./manage-app.sh restart      # Restart the application
./manage-app.sh status       # Check application status
./manage-app.sh logs         # View application logs
./manage-app.sh restore-db   # Restore database from dump
./manage-app.sh delete       # Delete everything (clean slate)
```

## Testing the Application

### 1. Homepage Testing
- Visit http://localhost:6600
- Verify product listings show "AI analyzed X reviews"
- Test search functionality with keywords like "dress", "shirt", "pants"
- Test filters (category, rating, division)

### 2. Product Detail Testing
- Click on any product to view details
- Verify AI reviews are separated into "Recommended" and "Not Recommended"
- Check that review counts match the homepage

### 3. Review Submission Testing
- Login with test account
- Submit a new review
- Verify real-time AI prediction appears
- Test override functionality

### 4. User Authentication Testing
- Test registration with new account
- Test login/logout functionality
- Test profile page access

## Troubleshooting

### Application Won't Start
```bash
# Check Docker status
docker-compose ps

# View logs
./manage-app.sh logs

# Restart everything
./manage-app.sh delete
./manage-app.sh setup
```

### Database Issues
```bash
# Restore database
./manage-app.sh restore-db

# Check database content
docker-compose exec web python -c "
from src.utils.database import get_database_connection
db = get_database_connection()
print(f'Products: {db.products.count_documents({})}')
print(f'Reviews: {db.reviews.count_documents({})}')
print(f'Users: {db.users.count_documents({})}')
"
```

### ML Models Not Working
```bash
# Check if models exist
ls -la models/

# Retrain models (if needed)
docker-compose exec web python src/train_models.py
```

## File Structure

```
asm3-online-shopping/
├── src/                    # Source code
│   ├── app/               # Flask application
│   ├── models/            # ML models and utilities
│   ├── utils/             # Helper utilities
│   └── config/            # Configuration files
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── migrate/               # Database migration scripts
│   └── mongodb_dump/      # Complete database dump
├── models/                # Pre-trained ML models
├── data/                  # CSV data files
├── documents/             # Documentation
├── manage-app.sh          # Main management script
├── startup_complete.sh    # Complete setup script
└── docker-compose.yml     # Docker configuration
```

## Support

If you encounter any issues:

1. Check the logs: `./manage-app.sh logs`
2. Verify Docker is running: `docker info`
3. Check application status: `./manage-app.sh status`
4. Restore database: `./manage-app.sh restore-db`

The application is designed to be fully functional on first startup with all data and ML predictions pre-loaded.

---

**Authors**: Hoang Chau Le <s3715228@rmit.edu.vn>, Bao Nguyen <s4139514@rmit.edu.vn>
