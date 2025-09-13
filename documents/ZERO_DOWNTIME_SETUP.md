# [START] Zero-Downtime Setup Guide

This guide shows how to run the Fashion Store application without downtime during restarts.

## [TARGET] Problem Solved

**Before:** Every container restart retrained ML models (5-10 minutes downtime)
**After:** Models are cached, application starts in seconds

##  Quick Start

### 1. First Time Setup (with training)
```bash
# Start everything (includes model training)
docker-compose up --build

# Or start only the web app (will train models if needed)
docker-compose up web --build
```

### 2. Subsequent Starts (no training)
```bash
# Start application (uses cached models)
docker-compose up web

# Restart application (no downtime)
docker-compose restart web
```

### 3. Retrain Models (when needed)
```bash
# Option 1: Delete models and restart
rm -rf models/
docker-compose up web

# Option 2: Use training service
docker-compose --profile training up trainer
```

## [PROCESS] How It Works

### Model Caching
- Models are saved to `./models/` directory
- Application checks if models exist before training
- If models exist, skips training and starts immediately

### Startup Process
1. **Check Models:** Look for existing model files
2. **Train if Needed:** Only train if models don't exist
3. **Check Database:** Verify data migration is complete
4. **Start App:** Launch Flask application

### File Structure
```
asm3-online-shopping/
├── models/                    # Cached ML models
│   ├── lr_model.pkl
│   ├── rf_model.pkl
│   ├── svm_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── spacy_embeddings.pkl
├── start_app.sh              # Smart startup script
├── train_models_once.py      # One-time training script
└── docker-compose.yml        # Updated with profiles
```

## ⚡ Performance Benefits

### Startup Times
- **First Run:** ~5-10 minutes (includes training)
- **Subsequent Runs:** ~10-30 seconds
- **Restart:** ~5-10 seconds

### Zero Downtime
- Models persist between restarts
- No retraining on container restart
- Fast application recovery

##  Commands Reference

### Development
```bash
# Start with training (first time)
docker-compose up --build

# Start without training (fast)
docker-compose up web

# Restart application
docker-compose restart web

# View logs
docker-compose logs web -f

# Stop everything
docker-compose down
```

### Model Management
```bash
# Check if models exist
ls -la models/

# Retrain models
rm -rf models/ && docker-compose up web

# Train models separately
docker-compose --profile training up trainer
```

### Database Management
```bash
# Reset database
docker-compose down -v
docker-compose up --build

# View database
docker-compose exec mongo mongosh
```

## 🚨 Troubleshooting

### Models Not Found
```bash
# Error: Models not found
# Solution: Train models first
docker-compose --profile training up trainer
```

### Database Empty
```bash
# Error: No products found
# Solution: Run migration
docker-compose exec web python migrate_products.py
```

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Rebuild container
docker-compose up --build web
```

## [DATA] Monitoring

### Check Application Status
```bash
# Health check
curl http://localhost:6600/api/stats

# View running containers
docker-compose ps
```

### Check Model Status
```bash
# List model files
docker-compose exec web ls -la models/

# Check model sizes
docker-compose exec web du -h models/
```

## [COMPLETE] Success!

Your application now starts in seconds instead of minutes! 

**Application URL:** http://localhost:6600
**Demo Account:** demo@fashionstore.com / hello
