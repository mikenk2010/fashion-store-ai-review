# Mass Update Reviews with ML Predictions

This guide explains how to apply machine learning predictions to all existing reviews in the Fashion Store database using the mass update functionality.

## Overview

The mass update feature allows you to retroactively apply ML predictions to all reviews in the database, including both individual reviews in the `reviews` collection and embedded reviews within product documents. This is useful for:

- Applying ML predictions to historical data
- Updating reviews that were created before ML models were implemented
- Ensuring consistency across all review data
- Recalculating product statistics based on ML predictions

## Features

### What the Mass Update Does

1. **Loads ML Models**: Automatically loads the trained ensemble models (Logistic Regression, Random Forest, SVM)
2. **Processes Individual Reviews**: Updates all reviews in the `reviews` collection
3. **Processes Embedded Reviews**: Updates all reviews embedded in product documents
4. **Applies ML Predictions**: Generates predictions, confidence scores, and detailed model results
5. **Recalculates Statistics**: Updates product statistics based on ML predictions
6. **Provides Verification**: Shows detailed statistics about the update process

### ML Prediction Details

For each review, the mass update applies:

- **Text Preprocessing**: Cleans and normalizes review text and title
- **Feature Extraction**: Generates BoW, embeddings, and TF-IDF features
- **Ensemble Prediction**: Combines predictions from all three models
- **Confidence Scoring**: Calculates confidence levels for predictions
- **Detailed Results**: Stores individual model results and voting details

## Usage

### Prerequisites

1. **Application Running**: The Fashion Store application must be running
2. **ML Models Available**: Trained models must be present in the `models/` directory
3. **Database Access**: MongoDB must be accessible and contain review data

### Running the Mass Update

#### Method 1: Using the Management Script (Recommended)

```bash
# Start the application if not already running
./manage-app.sh start

# Run the mass update
./manage-app.sh mass-update
```

The script will:
- Check if the application is running
- Ask for confirmation before proceeding
- Execute the mass update process
- Show progress and results

#### Method 2: Direct Script Execution

```bash
# Run the mass update script directly
python3 run_mass_update.py
```

#### Method 3: Manual Execution in Docker

```bash
# Execute the script inside the Docker container
docker-compose exec web python migrate/mass_update_reviews_ml.py
```

### Verification

After running the mass update, verify the results:

```bash
# Test the mass update results
python3 test_mass_update.py
```

This will show:
- Number of reviews updated
- Coverage percentage
- Sample predictions
- Overall statistics

## Script Details

### Main Mass Update Script

**File**: `migrate/mass_update_reviews_ml.py`

**Key Functions**:
- `load_ml_models()`: Loads the trained ML models
- `predict_review_ml()`: Applies ML prediction to a single review
- `update_individual_reviews()`: Updates reviews in the `reviews` collection
- `update_embedded_reviews()`: Updates embedded reviews in product documents
- `recalculate_product_stats()`: Recalculates product statistics
- `verify_updates()`: Verifies the update was successful

### Runner Script

**File**: `run_mass_update.py`

**Features**:
- Checks Docker status
- Verifies application is running
- Executes the mass update in the correct environment
- Provides error handling and status reporting

### Test Script

**File**: `test_mass_update.py`

**Features**:
- Verifies ML predictions were applied
- Shows coverage statistics
- Displays sample predictions
- Validates success criteria

## Database Updates

### Individual Reviews Collection

Each review in the `reviews` collection gets updated with:

```json
{
  "ml_prediction": 1,
  "ml_confidence": 0.85,
  "ml_details": {
    "ensemble_prediction": 1,
    "ensemble_confidence": 0.85,
    "individual_results": {
      "logistic_regression": {"prediction": 1, "confidence": 0.82},
      "random_forest": {"prediction": 1, "confidence": 0.87},
      "svm": {"prediction": 1, "confidence": 0.86}
    }
  },
  "prediction_timestamp": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Embedded Reviews in Products

Each embedded review gets updated with the same ML prediction fields, and the product document gets updated with:

```json
{
  "ml_recommended_count": 15,
  "ml_not_recommended_count": 3,
  "ml_recommendation_rate": 83.33,
  "avg_ml_confidence": 0.847,
  "stats_updated_at": "2024-01-01T12:00:00"
}
```

## Performance Considerations

### Processing Time

The mass update time depends on:
- **Number of reviews**: More reviews take longer to process
- **Review text length**: Longer reviews require more processing time
- **System resources**: CPU and memory availability
- **Database performance**: MongoDB query and update speed

**Estimated times**:
- 1,000 reviews: ~2-3 minutes
- 10,000 reviews: ~15-20 minutes
- 50,000 reviews: ~1-2 hours

### Batch Processing

The script processes reviews in batches of 100 to:
- Optimize memory usage
- Provide progress updates
- Handle large datasets efficiently
- Allow for graceful interruption

### Error Handling

The script includes comprehensive error handling:
- Continues processing if individual reviews fail
- Logs errors for debugging
- Provides detailed error messages
- Maintains data integrity

## Monitoring and Logs

### Progress Monitoring

The script provides real-time progress updates:
- Number of reviews processed
- Current batch being processed
- Estimated completion time
- Error counts and details

### Logging

All operations are logged to:
- Console output for real-time monitoring
- Application logs for detailed tracking
- Error logs for debugging issues

### Verification

After completion, the script provides:
- Summary statistics
- Coverage percentages
- Sample predictions
- Verification results

## Troubleshooting

### Common Issues

1. **ML Models Not Found**
   - Ensure models are trained and present in `models/` directory
   - Check file permissions and paths
   - Verify model file formats (.joblib)

2. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string in environment variables
   - Ensure database contains review data

3. **Memory Issues**
   - Reduce batch size in the script
   - Increase Docker memory allocation
   - Process reviews in smaller chunks

4. **Permission Issues**
   - Ensure scripts are executable
   - Check Docker container permissions
   - Verify file ownership

### Debugging

1. **Check Application Logs**
   ```bash
   ./manage-app.sh logs
   ```

2. **Verify Database State**
   ```bash
   python3 test_mass_update.py
   ```

3. **Test ML Models**
   ```bash
   docker-compose exec web python -c "from src.models import load_ml_models; print(load_ml_models())"
   ```

## Best Practices

### Before Running

1. **Backup Database**: Always backup your database before mass updates
2. **Test on Small Dataset**: Test with a subset of data first
3. **Verify ML Models**: Ensure models are properly trained and loaded
4. **Check System Resources**: Ensure adequate CPU and memory

### During Execution

1. **Monitor Progress**: Watch console output for progress updates
2. **Don't Interrupt**: Avoid stopping the process unless necessary
3. **Check Logs**: Monitor logs for any errors or warnings
4. **Verify Results**: Run verification tests after completion

### After Completion

1. **Verify Results**: Run the test script to verify success
2. **Check Statistics**: Verify product statistics are updated
3. **Test Application**: Ensure the application works correctly
4. **Monitor Performance**: Check if the application performance is affected

## Examples

### Basic Usage

```bash
# Start application
./manage-app.sh start

# Wait for application to be ready
sleep 30

# Run mass update
./manage-app.sh mass-update

# Verify results
python3 test_mass_update.py
```

### Advanced Usage

```bash
# Run with custom batch size (edit script)
# Edit migrate/mass_update_reviews_ml.py
# Change batch_size = 100 to batch_size = 50

# Run mass update
python3 run_mass_update.py

# Check specific product statistics
docker-compose exec web python -c "
from src.utils.database import get_database_connection
db = get_database_connection()
product = db.products.find_one({'title': 'Sample Product'})
print(f'ML Recommended: {product.get(\"ml_recommended_count\", 0)}')
print(f'ML Not Recommended: {product.get(\"ml_not_recommended_count\", 0)}')
print(f'ML Recommendation Rate: {product.get(\"ml_recommendation_rate\", 0)}%')
"
```

## Support

For issues or questions:

1. Check the application logs
2. Run the test script for verification
3. Review this documentation
4. Check the main application documentation

---

## Authors

- **Hoang Chau Le** <s3715228@rmit.edu.vn>
- **Bao Nguyen** <s4139514@rmit.edu.vn>

*RMIT University - Advanced Programming for Data Science*
