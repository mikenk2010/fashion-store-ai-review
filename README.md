# Fashion Store - AI-Powered E-commerce Application

A sophisticated Flask web application with ML-powered review classification, built with Docker and MongoDB.

## Quick Start

- Video

![Video Walkthru](./documents/screenshots/demo-shopping-review.gif)

- Homepage

![Home Page](./documents/screenshots/homepage.png)

- Review

![Review](./documents/screenshots/review.png)

![Review](./documents/screenshots/product-review-ai-rating.png)

![Review](./documents/screenshots/product-review-ai-rating-confirm.png)

### Prerequisites
- Docker and Docker Compose
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd asm3-online-shopping
   ```

2. **Start the application**
   ```bash
   ./manage-app.sh start
   ```

3. **Access the application**
   - **Application**: http://localhost:6600
   - **MongoDB**: mongodb://admin:password123@localhost:27017/ecommerce_db

### For Lecturers
See **[LECTURER_INSTRUCTIONS.md](LECTURER_INSTRUCTIONS.md)** for detailed evaluation instructions.

## Features

### Core Features
- **AI-Powered Review Classification**: ML models predict review sentiment
- **Product Browsing**: Search and filter clothing items
- **User Authentication**: Login, registration, and profile management
- **Wishlist**: Save favorite products
- **Real-time Predictions**: Live review sentiment analysis
- **Responsive Design**: Modern, mobile-friendly interface

### Machine Learning
- **Ensemble Models**: Logistic Regression, Random Forest, and SVM
- **Multiple Features**: Bag-of-Words, spaCy embeddings, TF-IDF
- **Confidence Scoring**: Model prediction confidence levels
- **User Override**: Manual prediction override capability

### Architecture
- **Flask Web Framework**: RESTful API and web interface
- **MongoDB Database**: NoSQL document storage
- **Docker Containerization**: Easy deployment and scaling
- **Modular Design**: Clean, maintainable code structure

## Management Commands

Use the unified management script for all operations:

```bash
# Start the application
./manage-app.sh start

# Start in development mode (with file sync)
./manage-app.sh start-dev

# Restart the application
./manage-app.sh restart

# Stop the application
./manage-app.sh stop

# Show application status
./manage-app.sh status

# View logs
./manage-app.sh logs

# Run tests
./manage-app.sh test

# Run database migrations
./manage-app.sh migrate

# Delete application and data
./manage-app.sh delete

# Show help
./manage-app.sh help
```

## Project Structure

```
asm3-online-shopping/
├── src/                    # Source code
│   ├── app/               # Flask application
│   ├── config/            # Configuration
│   ├── models/            # ML models
│   └── utils/             # Utilities
├── migrate/               # Database migrations
├── tests/                 # Test suite
├── templates/             # HTML templates
├── static/                # Static assets
├── data/                  # Data files
├── models/                # Trained ML models
├── logs/                  # Application logs
├── documents/             # Documentation
├── manage-app.sh          # Management script
├── main.py                # Production application entry point
├── docker-compose.yml     # Production Docker Compose
├── docker-compose.dev.yml # Development Docker Compose
└── README.md              # This file
```

## Testing

### Run Tests
```bash
./manage-app.sh test
```

### Test Coverage
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **ML Tests**: Model prediction testing
- **Auth Tests**: Authentication flow testing

## Database

### Collections
- **products**: Clothing items with embedded reviews
- **users**: User accounts and wishlists
- **reviews**: Individual review records

### Migrations
```bash
# Run all migrations
./manage-app.sh migrate

# Run specific migration
docker-compose exec web python migrate/run_migrations.py --migration products
```

## Configuration

### Environment Variables
Create a `.env` file with:
```env
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://admin:password123@mongo:27017/ecommerce_db
HOST=0.0.0.0
PORT=6600
LOG_LEVEL=INFO
```

### Development vs Production
- **Development**: File sync enabled, debug mode
- **Production**: Optimized for performance, secure settings

## Documentation

Comprehensive documentation is available in the `documents/` folder:

- **[Development Guide](documents/DEVELOPMENT_GUIDE.md)** - Development workflow and setup
- **[Implementation Summary](documents/IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[Refactored Structure](documents/REFACTORED_STRUCTURE.md)** - Code organization and architecture
- **[Quick Start Guide](documents/QUICK_START.md)** - Quick setup instructions
- **[Zero Downtime Setup](documents/ZERO_DOWNTIME_SETUP.md)** - Production deployment guide
- **[Cleanup Summary](documents/CLEANUP_SUMMARY.md)** - Code cleanup and optimization

## Deployment

### Development
```bash
./manage-app.sh start-dev
```

### Production
```bash
./manage-app.sh start
```

### Docker Commands
```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop and remove
docker-compose down
```

## Monitoring

### Application Status
```bash
./manage-app.sh status
```

### Logs
```bash
# Follow logs
./manage-app.sh logs

# Last 100 lines
./manage-app.sh logs-tail
```

### Health Checks
- Application: http://localhost:6600/
- MongoDB: mongodb://admin:password123@localhost:27017/ecommerce_db

## Development

### Entry Points
- **Production**: `python main.py` - Used by Docker containers
- **Development**: `python -m src` - For local development with package imports

### File Structure
- **Modular Design**: Clean separation of concerns
- **Blueprint Pattern**: Organized route handling
- **Factory Pattern**: Application creation
- **Configuration Classes**: Environment-specific settings

### Code Quality
- **Type Hints**: Better code clarity
- **Documentation**: Comprehensive code comments
- **Testing**: Unit and integration tests
- **Logging**: Structured logging system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./manage-app.sh test`
5. Submit a pull request

## License

This project is part of an academic assignment for RMIT University.

## Academic Context

**Course**: COSC3082 - Advanced Programming for Data Science  
**Assignment**: Milestone II - Web-based Data Application  
**Features**: ML-powered review classification, Docker containerization, MongoDB integration

## Support

For issues and questions:
1. Check the documentation in `documents/`
2. Run `./manage-app.sh help` for command help
3. Check logs with `./manage-app.sh logs`
4. Verify status with `./manage-app.sh status`

---

**Built for RMIT University Advanced Programming for Data Science**