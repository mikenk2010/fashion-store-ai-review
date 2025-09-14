# Fashion Store Dataset - Exploratory Data Analysis


## Authors

- **Hoang Chau Le** <s3715228@rmit.edu.vn>
- **Bao Nguyen** <s4139514@rmit.edu.vn>

## Overview

This document presents a comprehensive exploratory data analysis (EDA) of the Fashion Store clothing review dataset. The analysis reveals key insights about customer behavior, product performance, and review patterns that inform the machine learning models and business decisions.

## Dataset Information

- **Total Reviews**: 19,662
- **Products**: 1,095 unique clothing items
- **Features**: 12 columns including ratings, reviews, demographics, and product information
- **Time Period**: Historical customer review data
- **Data Quality**: No missing values detected

## Key Findings Summary

| Metric | Value | Insight |
|--------|-------|---------|
| Average Rating | 4.18/5.0 | High customer satisfaction |
| Recommendation Rate | 81.8% | Strong product approval |
| Most Reviewed Department | Tops (8,713 reviews) | Popular product category |
| Average Customer Age | 43.3 years | Mature customer base |
| Average Review Length | 318 characters | Detailed customer feedback |

## 1. Rating Distribution Analysis

### Distribution Overview
The dataset shows a strong positive bias in customer ratings:

- **5-star ratings**: 10,858 reviews (55.2%)
- **4-star ratings**: 4,289 reviews (21.8%)
- **3-star ratings**: 2,464 reviews (12.5%)
- **2-star ratings**: 1,360 reviews (6.9%)
- **1-star ratings**: 691 reviews (3.5%)

### Key Insights
- **High satisfaction**: 77% of reviews are 4-5 stars
- **Low dissatisfaction**: Only 10.4% of reviews are 1-2 stars
- **Median rating**: 5.0 (perfect score)
- **Positive skew**: Distribution heavily favors positive ratings

![Rating Distribution](../static/images/eda/rating_distribution.png)

## 2. Recommendation Analysis

### Recommendation Patterns
The recommendation system shows strong alignment with ratings:

- **Recommended (1)**: 16,087 reviews (81.8%)
- **Not Recommended (0)**: 3,575 reviews (18.2%)

### Key Insights
- **High recommendation rate**: Over 4 in 5 customers recommend products
- **Strong positive sentiment**: Recommendation rate closely follows rating distribution
- **Business impact**: High recommendation rate indicates strong product quality

![Recommendation Distribution](../static/images/eda/recommendation_distribution.png)

## 3. Rating vs Recommendation Correlation

### Cross-tabulation Analysis
The relationship between ratings and recommendations shows clear patterns:

| Rating | Not Recommended | Recommended | Total | Rec. Rate |
|--------|----------------|-------------|-------|-----------|
| 1 | 684 | 7 | 691 | 1.0% |
| 2 | 1,280 | 80 | 1,360 | 5.9% |
| 3 | 1,444 | 1,020 | 2,464 | 41.4% |
| 4 | 146 | 4,143 | 4,289 | 96.6% |
| 5 | 21 | 10,837 | 10,858 | 99.8% |

### Key Insights
- **Strong correlation**: Rating and recommendation are highly correlated (0.793)
- **Threshold effect**: 4+ star ratings almost always result in recommendations
- **ML model relevance**: This correlation validates the ML approach for prediction

![Rating vs Recommendation](../static/images/eda/rating_vs_recommendation.png)

## 4. Department Performance Analysis

### Department Distribution
Product categories show varying levels of customer engagement:

| Department | Review Count | Avg Rating | Rec. Rate |
|------------|--------------|------------|-----------|
| Tops | 8,713 | 4.16 | 80.9% |
| Dresses | 5,371 | 4.14 | 80.3% |
| Bottoms | 3,184 | 4.29 | 85.3% |
| Intimate | 1,408 | 4.26 | 84.6% |
| Jackets | 879 | 4.27 | 84.1% |
| Trend | 107 | 3.86 | 75.7% |

### Key Insights
- **Tops dominance**: 44% of all reviews are for tops
- **Bottoms excellence**: Highest average rating (4.29) and recommendation rate (85.3%)
- **Trend challenges**: Lowest performance across all metrics
- **Consistent quality**: Most departments maintain 4+ star averages

![Department Analysis](../static/images/eda/department_analysis.png)

## 5. Customer Demographics Analysis

### Age Distribution
The customer base shows a mature demographic profile:

- **Average age**: 43.3 years
- **Age range**: 18-99 years
- **Median age**: 41 years
- **Standard deviation**: 12.3 years

### Age vs Rating Analysis
Different age groups show varying satisfaction levels:

| Age Group | Count | Avg Rating |
|-----------|-------|------------|
| 18-34 | 5,069 | 4.14 |
| 35-50 | 9,281 | 4.16 |
| 51-67 | 4,586 | 4.25 |
| 68-83 | 658 | 4.24 |
| 84-99 | 68 | 4.53 |

### Key Insights
- **Mature customer base**: Average age of 43.3 years
- **Age-satisfaction correlation**: Older customers tend to give higher ratings
- **Stable demographics**: Most customers are in the 35-50 age range

![Age Distribution](../static/images/eda/age_distribution.png)

## 6. Text Analysis

### Review Length Patterns
Customer reviews show detailed feedback patterns:

**Review Text Length:**
- **Average length**: 318 characters
- **Median length**: 315 characters
- **Range**: 9-508 characters
- **Standard deviation**: 142 characters

**Title Length:**
- **Average length**: 19 characters
- **Median length**: 17 characters
- **Range**: 2-52 characters
- **Standard deviation**: 10 characters

### Key Insights
- **Detailed feedback**: Average review length indicates thoughtful customer input
- **Consistent patterns**: Review length shows normal distribution
- **Quality indicators**: Longer reviews may indicate higher engagement

![Text Length Analysis](../static/images/eda/text_length_analysis.png)

## 7. Correlation Analysis

### Feature Correlations
The correlation matrix reveals important relationships:

| Feature 1 | Feature 2 | Correlation | Significance |
|-----------|-----------|-------------|--------------|
| Rating | Recommended IND | 0.793 | Very strong positive |
| Rating | Age | 0.035 | Weak positive |
| Review Length | Positive Feedback | 0.193 | Moderate positive |
| Title Length | Review Length | 0.225 | Moderate positive |
| Age | Positive Feedback | 0.041 | Weak positive |

### Key Insights
- **Rating-Recommendation**: Strong correlation validates ML model approach
- **Age-Rating**: Weak correlation suggests age doesn't strongly influence satisfaction
- **Text Engagement**: Longer reviews receive more positive feedback
- **Content Quality**: Title and review length are moderately correlated

![Correlation Matrix](../static/images/eda/correlation_matrix.png)

## 8. Business Intelligence Insights

### Customer Satisfaction Drivers
1. **Product Quality**: High average ratings (4.18) indicate strong product quality
2. **Department Performance**: Bottoms and Intimate categories show highest satisfaction
3. **Customer Engagement**: Detailed reviews (318 chars avg) show high engagement
4. **Recommendation Culture**: 81.8% recommendation rate indicates strong brand loyalty

### Product Performance Indicators
1. **Top Performers**: Bottoms (4.29 avg rating, 85.3% rec rate)
2. **Growth Opportunities**: Trend category needs improvement (3.86 avg rating)
3. **Volume Leaders**: Tops category drives most engagement (8,713 reviews)
4. **Quality Consistency**: Most departments maintain 4+ star averages

### Machine Learning Implications
1. **Model Validation**: Strong rating-recommendation correlation (0.793) validates ML approach
2. **Feature Engineering**: Text length and department are important features
3. **Class Imbalance**: 81.8% positive recommendations require balanced training
4. **Prediction Confidence**: High correlation enables confident predictions

## 9. Data Quality Assessment

### Completeness
- **No missing values**: All 19,662 records are complete
- **Data integrity**: All required fields populated
- **Consistency**: Data types and formats are consistent

### Accuracy
- **Rating validation**: All ratings are within 1-5 range
- **Age validation**: All ages are within reasonable 18-99 range
- **Text validation**: All text fields contain meaningful content

### Reliability
- **Temporal consistency**: Data shows consistent patterns over time
- **Logical consistency**: Rating and recommendation patterns align logically
- **Statistical validity**: Distributions follow expected patterns

## 10. Recommendations for ML Model Development

### Feature Selection
1. **Primary features**: Rating, review text, title, department
2. **Secondary features**: Age, review length, positive feedback count
3. **Derived features**: Text sentiment, department performance scores

### Model Considerations
1. **Class balancing**: Address 81.8% positive class imbalance
2. **Ensemble approach**: Use multiple models for robust predictions
3. **Confidence scoring**: Implement uncertainty quantification
4. **Feature scaling**: Normalize numerical features for optimal performance

### Validation Strategy
1. **Cross-validation**: Use stratified sampling for balanced validation
2. **Holdout testing**: Reserve 20% of data for final model evaluation
3. **Performance metrics**: Focus on precision, recall, and F1-score
4. **Business metrics**: Align model performance with business objectives

## Conclusion

The EDA reveals a high-quality dataset with strong customer satisfaction patterns. The 81.8% recommendation rate and 4.18 average rating indicate excellent product quality and customer experience. The strong correlation between ratings and recommendations (0.793) validates the machine learning approach for automated recommendation prediction.

Key opportunities include improving the Trend category performance and leveraging the detailed customer feedback for product development. The mature customer base (43.3 years average) suggests a stable market with high engagement levels.

The analysis provides a solid foundation for developing robust machine learning models that can accurately predict customer recommendations while maintaining high confidence levels for business decision-making.

---

*RMIT University - Advanced Programming for Data Science*
