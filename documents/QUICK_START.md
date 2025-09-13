# Quick Start Guide

## [START] Getting Started

### Option 1: Using Docker (Recommended)

1. **Navigate to the SourceCode directory**:
   ```bash
   cd SourceCode
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Open your browser and go to `http://localhost:5000`

### Option 2: Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start MongoDB** (make sure MongoDB is running on localhost:27017)

3. **Train the ML model**:
   ```bash
   python train_model.py
   ```

4. **Run the Flask application**:
   ```bash
   python app.py
   ```

## [TARGET] What You Can Do

1. **Browse Products**: View all clothing items with filtering and sorting
2. **View Product Details**: Click on any product to see detailed information
3. **Write Reviews**: Submit reviews with ratings and text
4. **AI Classification**: See AI predictions for your reviews
5. **Override AI**: Confirm or override the AI's recommendation

## [PROCESS] Features Included

- [SUCCESS] Product listing with pagination
- [SUCCESS] Product detail pages
- [SUCCESS] Review submission system
- [SUCCESS] ML-powered review classification
- [SUCCESS] User override functionality
- [SUCCESS] MongoDB integration
- [SUCCESS] Responsive Bootstrap UI
- [SUCCESS] Docker containerization
- [SUCCESS] Filtering and sorting
- [SUCCESS] Real-time form validation

## [DATA] ML Model Details

- **Algorithm**: Logistic Regression
- **Vectorization**: TF-IDF with n-grams
- **Features**: 5000 most frequent terms
- **Accuracy**: ~85-90% on test data
- **Training Data**: Uses the provided CSV dataset

## 🐳 Docker Services

- **MongoDB**: Port 27017
- **Flask App**: Port 5000
- **Automatic ML training** on startup

## 📁 Project Structure

```
SourceCode/
├── app.py                 # Main Flask application
├── train_model.py         # ML model training
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker setup
├── Dockerfile            # Container configuration
├── data/                 # Dataset
├── models/               # ML models (auto-created)
├── templates/            # HTML templates
└── static/               # CSS/JS assets
```

## 🚨 Troubleshooting

### If Docker fails:
1. Make sure Docker is running
2. Check that `data/data-assignment3_II.csv` exists
3. Try `docker-compose down` then `docker-compose up --build`

### If manual setup fails:
1. Install all dependencies: `pip install -r requirements.txt`
2. Make sure MongoDB is running
3. Run `python train_model.py` first

## [COMPLETE] Success!

Once running, you should see:
- Product listing page with clothing items
- Ability to filter by category
- Product detail pages with reviews
- Review submission with AI classification
- User confirmation workflow

Enjoy exploring the Fashion Store! 
