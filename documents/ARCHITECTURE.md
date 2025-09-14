# Fashion Store - System Architecture


## Authors

- **Hoang Chau Le** <s3715228@rmit.edu.vn>
- **Bao Nguyen** <s4139514@rmit.edu.vn>

## Overview

The Fashion Store is a modern e-commerce web application built with Flask, MongoDB, and Docker. It features AI-powered review classification using ensemble machine learning models and provides a comprehensive shopping experience with user authentication, product browsing, and review management.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (HTML/CSS/JavaScript)                             │
│  - Responsive UI with Bootstrap 5                              │
│  - Real-time ML prediction feedback                            │
│  - Interactive product browsing and filtering                  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Flask Web Application (Python 3.11)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Main Routes   │  │   API Routes    │  │  Auth Routes    │ │
│  │   - Homepage    │  │   - Products    │  │  - Login        │ │
│  │   - Products    │  │   - Predictions │  │  - Register     │ │
│  │   - Reviews     │  │   - Statistics  │  │  - Profile      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   ML Models     │  │   Utilities     │  │   Database      │ │
│  │   - Ensemble    │  │   - Auth        │  │   - Connection  │ │
│  │   - LR/RF/SVM   │  │   - Helpers     │  │   - Queries     │ │
│  │   - Preprocessing│  │   - Logging    │  │   - Migrations  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ MongoDB Protocol
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  MongoDB Database (NoSQL)                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Products      │  │     Users       │  │    Sessions     │ │
│  │   - Clothing ID │  │   - User ID     │  │   - Session ID  │ │
│  │   - Details     │  │   - Credentials │  │   - User Data   │ │
│  │   - Reviews     │  │   - Profile     │  │   - Timestamps  │ │
│  │   - Images      │  │   - Preferences │  │   - Expiry      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Docker Network
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Docker Containers                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Web App       │  │   MongoDB       │  │   File System   │ │
│  │   - Flask       │  │   - Database    │  │   - Static Files│ │
│  │   - Python 3.11 │  │   - Collections │  │   - Images      │ │
│  │   - Port 6600   │  │   - Port 27017  │  │   - Logs        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer

**Technology Stack:**
- HTML5 with Jinja2 templating
- Bootstrap 5 for responsive design
- JavaScript (ES6+) for interactivity
- CSS3 for custom styling

**Key Components:**
- **Product Listing Page**: Displays products with filtering and pagination
- **Product Detail Page**: Shows individual product information and reviews
- **Review Submission Form**: Allows users to submit reviews with real-time ML feedback
- **Review Confirmation Page**: Handles ML prediction override functionality
- **User Authentication**: Login/register forms with session management
- **Statistics Dashboard**: Displays application metrics and analytics

**Features:**
- Real-time ML prediction as users type reviews
- Responsive design for mobile and desktop
- Interactive filtering and search functionality
- Dynamic content loading with AJAX
- Form validation and error handling

### 2. Backend Layer

**Technology Stack:**
- Python 3.11
- Flask web framework
- Blueprint-based modular architecture
- RESTful API design

**Core Modules:**

#### 2.1 Application Factory (`src/app/factory.py`)
- Centralized application configuration
- Blueprint registration
- Database initialization
- Error handling setup

#### 2.2 Route Handlers
- **Main Routes** (`src/app/routes/main.py`): Core application routes
- **API Routes** (`src/app/routes/api.py`): RESTful API endpoints
- **Auth Routes** (`src/app/routes/auth.py`): User authentication

#### 2.3 Machine Learning Module (`src/models/`)
- **Review Classifier** (`review_classifier.py`): Ensemble ML model
- **Model Training** (`train_models.py`): Model training and evaluation
- **Feature Engineering**: Text preprocessing and feature extraction

#### 2.4 Utility Modules (`src/utils/`)
- **Database** (`database.py`): MongoDB connection and operations
- **Authentication** (`auth.py`): User session management
- **Helpers** (`helpers.py`): Common utility functions
- **Complete Setup** (`complete_setup.py`): Automated data loading

### 3. Data Layer

**Database: MongoDB (NoSQL)**
- **Products Collection**: Product information with embedded reviews
- **Users Collection**: User accounts and profiles
- **Sessions**: User session management

**Data Models:**

#### 3.1 Product Document
```json
{
  "_id": "ObjectId",
  "clothing_id": 123,
  "title": "Product Name",
  "description": "Product Description",
  "division_name": "General",
  "department_name": "Dresses",
  "class_name": "Dresses",
  "category": "Dresses",
  "avg_rating": 4.2,
  "review_count": 15,
  "reviews": [
    {
      "user_id": "user123",
      "user_name": "John Doe",
      "rating": 5,
      "title": "Great product!",
      "text": "I love this dress...",
      "ml_prediction": 1,
      "final_decision": 1,
      "user_override": null,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 3.2 User Document
```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "hashed_password",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. Machine Learning Architecture

**Ensemble Model System:**
- **Logistic Regression**: Bag-of-Words features
- **Random Forest**: spaCy word embeddings
- **Support Vector Machine**: TF-IDF weighted embeddings
- **Majority Voting**: Final prediction decision
- **Confidence Scoring**: Model uncertainty quantification

**Feature Engineering Pipeline:**
1. **Text Preprocessing**: Cleaning, tokenization, normalization
2. **Feature Extraction**: BoW, embeddings, TF-IDF
3. **Feature Scaling**: Standardization for numerical features
4. **Model Training**: Cross-validation and hyperparameter tuning
5. **Model Persistence**: Joblib serialization for deployment

**Prediction Flow:**
```
User Input → Text Preprocessing → Feature Extraction → 
Model Prediction → Ensemble Voting → Confidence Calculation → 
User Override Option → Final Decision → Database Storage
```

### 5. Infrastructure Layer

**Containerization: Docker**
- **Multi-container setup** with Docker Compose
- **Web Application Container**: Flask app with Python 3.11
- **Database Container**: MongoDB 7.0
- **Volume Management**: Persistent data storage
- **Network Configuration**: Internal container communication

**Deployment Architecture:**
- **Development Mode**: File synchronization for live development
- **Production Mode**: Optimized for performance and security
- **Health Checks**: Container health monitoring
- **Logging**: Centralized logging system

## Data Flow Architecture

### 1. User Registration/Login Flow
```
User → Registration Form → Validation → Password Hashing → 
MongoDB Users Collection → Session Creation → Redirect to Homepage
```

### 2. Product Browsing Flow
```
User → Homepage → Product Listing → Filter/Search → 
MongoDB Query → Product Data → Template Rendering → User View
```

### 3. Review Submission Flow
```
User → Product Detail → Review Form → Real-time ML Prediction → 
Review Confirmation → User Override Option → Final Decision → 
MongoDB Update → Redirect to Product Page
```

### 4. ML Prediction Flow
```
Review Text → Text Preprocessing → Feature Extraction → 
Model 1 (LR) → Model 2 (RF) → Model 3 (SVM) → 
Ensemble Voting → Confidence Calculation → API Response
```

## Security Architecture

### 1. Authentication & Authorization
- **Session-based authentication** with secure cookies
- **Password hashing** using secure algorithms
- **Route protection** with decorators
- **CSRF protection** for form submissions

### 2. Data Security
- **Input validation** and sanitization
- **SQL injection prevention** (NoSQL injection protection)
- **XSS protection** with template escaping
- **Secure headers** configuration

### 3. Infrastructure Security
- **Container isolation** with Docker
- **Network segmentation** with Docker networks
- **Environment variable** management
- **Secret management** for sensitive data

## Performance Architecture

### 1. Database Optimization
- **Indexing strategy** for frequently queried fields
- **Embedded documents** for related data
- **Query optimization** with proper aggregation
- **Connection pooling** for database connections

### 2. Caching Strategy
- **Static file caching** for images and CSS
- **Session caching** for user data
- **Model caching** for ML predictions
- **Template caching** for rendered pages

### 3. Scalability Considerations
- **Horizontal scaling** with multiple container instances
- **Load balancing** for high traffic
- **Database sharding** for large datasets
- **CDN integration** for static assets

## Monitoring & Logging

### 1. Application Logging
- **Structured logging** with different levels
- **Request/response logging** for debugging
- **Error tracking** with stack traces
- **Performance metrics** collection

### 2. System Monitoring
- **Container health checks** for availability
- **Resource usage monitoring** (CPU, memory, disk)
- **Database performance** monitoring
- **ML model performance** tracking

## Development & Deployment

### 1. Development Workflow
- **Version control** with Git
- **Code quality** with linting and formatting
- **Testing strategy** with unit and integration tests
- **Documentation** with comprehensive guides

### 2. Deployment Strategy
- **Container-based deployment** with Docker
- **Environment configuration** management
- **Database migrations** automation
- **Zero-downtime deployment** capability

### 3. Maintenance & Updates
- **Automated setup** for new environments
- **Data backup** and recovery procedures
- **Model retraining** pipeline
- **Security updates** management

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 | User interface and interaction |
| Backend | Python 3.11, Flask | Web application framework |
| Database | MongoDB 7.0 | NoSQL data storage |
| ML/AI | scikit-learn, spaCy, pandas | Machine learning and NLP |
| Containerization | Docker, Docker Compose | Application deployment |
| Infrastructure | Linux, Docker Engine | Runtime environment |
| Monitoring | Python logging, Docker health checks | System monitoring |

This architecture provides a robust, scalable, and maintainable foundation for the Fashion Store e-commerce application, ensuring high performance, security, and user experience.

---

*RMIT University - Advanced Programming for Data Science*
