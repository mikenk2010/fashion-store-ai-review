# Lecturer Instructions - Fashion Store Application

## Quick Start for Evaluation

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### 1. Start the Application
```bash
./manage-app.sh start
```

### 2. Access the Application
- **Application**: http://localhost:6600
- **MongoDB**: mongodb://admin:password123@localhost:27017/ecommerce_db

### 3. Test Key Features
1. **Browse Products**: Homepage shows clothing items with search/filter
2. **User Registration**: Create account with name, email, password
3. **Product Details**: Click any product to see details and reviews
4. **ML Prediction**: Try submitting a review to see AI classification
5. **User Profile**: Access profile page to edit information
6. **Wishlist**: Add products to wishlist

### 4. Stop the Application
```bash
./manage-app.sh stop
```

## Application Features

### Machine Learning
- **3-Model Ensemble**: Logistic Regression, Random Forest, SVM
- **Real-time Prediction**: Live review sentiment analysis
- **Confidence Scoring**: Model prediction confidence levels
- **User Override**: Manual prediction override capability

### E-commerce Features
- **Product Browsing**: Search and filter clothing items
- **User Authentication**: Login, registration, profile management
- **Wishlist**: Save favorite products
- **Review System**: Submit and view product reviews

### Technical Features
- **Docker Containerization**: Easy deployment and scaling
- **MongoDB Database**: NoSQL document storage
- **Responsive Design**: Modern, mobile-friendly interface
- **Comprehensive Logging**: Detailed application logs

## Data Information

- **Products**: 23,486 clothing items from CSV dataset
- **Reviews**: Embedded reviews with ML predictions
- **Images**: 1,000+ product images organized by category
- **Users**: Demo accounts available for testing

## Demo Accounts

### Test User 1
- **Email**: test@example.com
- **Password**: test123

### Test User 2
- **Email**: demo@fashion.com
- **Password**: demo123

## Management Commands

```bash
# Start application
./manage-app.sh start

# Start in development mode
./manage-app.sh start-dev

# Check status
./manage-app.sh status

# View logs
./manage-app.sh logs

# Run tests
./manage-app.sh test

# Stop application
./manage-app.sh stop

# Delete everything
./manage-app.sh delete
```

## Troubleshooting

### Application Not Starting
1. Check Docker is running: `docker info`
2. Check logs: `./manage-app.sh logs`
3. Check status: `./manage-app.sh status`

### Database Issues
1. Check MongoDB connection: `mongodb://admin:password123@localhost:27017/ecommerce_db`
2. Restart application: `./manage-app.sh restart`

### ML Prediction Issues
1. Check if models are loaded: Look for model files in `models/` directory
2. Check logs for ML-related errors
3. Restart application to retrain models

## Project Structure

```
asm3-online-shopping/
├── src/                    # Source code (refactored)
├── migrate/               # Database migrations
├── tests/                 # Test suite
├── templates/             # HTML templates
├── static/                # Static assets (CSS, JS, images)
├── data/                  # Data files (CSV)
├── models/                # Trained ML models
├── logs/                  # Application logs
├── documents/             # Detailed documentation
├── manage-app.sh          # Management script
├── main.py                # Application entry point
└── README.md              # Main documentation
```

## Evaluation Criteria

### Technical Implementation
- **ML Models**: 3-model ensemble with different feature representations
- **Docker**: Proper containerization and orchestration
- **Database**: MongoDB integration with proper data modeling
- **API**: RESTful API design with proper error handling

### Code Quality
- **Structure**: Clean, modular code organization
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear documentation and comments
- **Logging**: Structured logging system

### User Experience
- **Interface**: Modern, responsive design
- **Functionality**: All features working correctly
- **Performance**: Fast loading and response times
- **Usability**: Intuitive user interface

## Contact

For any questions or issues during evaluation, please refer to the comprehensive documentation in the `documents/` folder or check the application logs.

---

**Good luck with your evaluation!**
