// Fashion Store Main JavaScript

// Global variables
let predictionTimeout;
let currentFilters = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize view toggles
    initializeViewToggles();
    
    // Initialize real-time features
    initializeRealTimeFeatures();
    
    // Initialize statistics
    loadStatistics();
    
    console.log('[START] Fashion Store App initialized');
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeFormHandlers() {
    // Auto-submit filter forms
    const filterForms = document.querySelectorAll('form[data-auto-submit]');
    filterForms.forEach(form => {
        form.addEventListener('change', function() {
            showLoadingState();
            this.submit();
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showFormErrors(form);
            }
            form.classList.add('was-validated');
        });
    });
}

function initializeViewToggles() {
    const gridView = document.getElementById('gridView');
    const listView = document.getElementById('listView');
    const productsContainer = document.getElementById('productsContainer');
    
    if (gridView && listView && productsContainer) {
        gridView.addEventListener('click', function() {
            switchToGridView();
        });
        
        listView.addEventListener('click', function() {
            switchToListView();
        });
    }
}

function switchToGridView() {
    const gridView = document.getElementById('gridView');
    const listView = document.getElementById('listView');
    const productsContainer = document.getElementById('productsContainer');
    const productItems = productsContainer.querySelectorAll('.product-item');
    
    gridView.classList.add('active');
    listView.classList.remove('active');
    productsContainer.className = 'row';
    
    productItems.forEach(item => {
        item.className = 'col-lg-4 col-md-6 mb-4 product-item';
    });
    
    // Save preference
    localStorage.setItem('viewPreference', 'grid');
}

function switchToListView() {
    const gridView = document.getElementById('gridView');
    const listView = document.getElementById('listView');
    const productsContainer = document.getElementById('productsContainer');
    const productItems = productsContainer.querySelectorAll('.product-item');
    
    listView.classList.add('active');
    gridView.classList.remove('active');
    productsContainer.className = 'row';
    
    productItems.forEach(item => {
        item.className = 'col-12 mb-3 product-item';
    });
    
    // Save preference
    localStorage.setItem('viewPreference', 'list');
}

function initializeRealTimeFeatures() {
    // Real-time search
    const searchInput = document.getElementById('search');
        if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            performSearch(this.value);
        }, 500));
    }
    
    // Real-time prediction for review forms
    const reviewTextArea = document.getElementById('review_text');
    if (reviewTextArea) {
        reviewTextArea.addEventListener('input', function() {
            handleReviewTextInput(this.value);
            });
        }
    }

function performSearch(query) {
    if (query.length < 2) return;
    
    showLoadingState();
    
    // Update URL with search query
    const url = new URL(window.location);
    url.searchParams.set('search', query);
    window.history.pushState({}, '', url);
    
    // Submit form
    const form = document.getElementById('filterForm');
    if (form) {
        form.submit();
    }
}

function handleReviewTextInput(reviewText) {
    // Clear previous timeout
    if (predictionTimeout) {
        clearTimeout(predictionTimeout);
    }
    
    // Show prediction result if text is long enough
    if (reviewText.trim().length > 10) {
        document.getElementById('predictionResult').style.display = 'block';
        showPredictionLoading();
        
        // Set timeout for API call
        predictionTimeout = setTimeout(() => {
            predictReview(reviewText);
        }, 1000);
    } else {
        document.getElementById('predictionResult').style.display = 'none';
    }
}

function showPredictionLoading() {
    const predictionLabel = document.getElementById('predictionLabel');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceBar = document.getElementById('confidenceBar');
    
    if (predictionLabel) predictionLabel.textContent = 'Analyzing...';
    if (confidenceValue) confidenceValue.textContent = '0%';
    if (confidenceBar) {
        confidenceBar.style.width = '0%';
        confidenceBar.className = 'progress-bar';
    }
}

function predictReview(reviewText) {
    // Get title and rating from the form
    const title = document.getElementById('title') ? document.getElementById('title').value : '';
    const rating = document.getElementById('rating') ? document.getElementById('rating').value : '';
    
    fetch('/api/predict_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            review_text: reviewText,
            title: title,
            rating: rating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Prediction error:', data.error);
            showPredictionError(data.error);
            return;
        }
        
        updatePredictionDisplay(data);
    })
    .catch(error => {
        console.error('Error:', error);
        showPredictionError('Failed to analyze review');
    });
}

function updatePredictionDisplay(data) {
    const prediction = data.prediction;
    const confidence = data.confidence;
    const label = data.label;
    
    // Update main prediction
    const badge = document.getElementById('predictionBadge');
    const predictionLabel = document.getElementById('predictionLabel');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceBar = document.getElementById('confidenceBar');
    
    if (badge) {
        badge.textContent = label;
        badge.className = `badge bg-${prediction ? 'success' : 'danger'}`;
    }
    
    if (predictionLabel) predictionLabel.textContent = label;
    if (confidenceValue) confidenceValue.textContent = `${(confidence * 100).toFixed(1)}%`;
    
    if (confidenceBar) {
        confidenceBar.style.width = `${confidence * 100}%`;
        confidenceBar.className = `progress-bar bg-${prediction ? 'success' : 'danger'}`;
    }
    
    // Update individual model results
    if (data.details && data.details.individual_results) {
        updateIndividualResults(data.details.individual_results);
    }
    
    // Add animation
    const predictionResult = document.getElementById('predictionResult');
    if (predictionResult) {
        predictionResult.classList.add('ai-prediction');
    }
}

function updateIndividualResults(results) {
    const lrResult = document.getElementById('lrResult');
    const rfResult = document.getElementById('rfResult');
    const svmResult = document.getElementById('svmResult');
    
    if (lrResult) {
        const lr = results.logistic_regression;
        lrResult.textContent = `${lr.label} (${(lr.confidence * 100).toFixed(0)}%)`;
    }
    
    if (rfResult) {
        const rf = results.random_forest;
        rfResult.textContent = `${rf.label} (${(rf.confidence * 100).toFixed(0)}%)`;
    }
    
    if (svmResult) {
        const svm = results.svm;
        svmResult.textContent = `${svm.label} (${(svm.confidence * 100).toFixed(0)}%)`;
    }
}

function showPredictionError(error) {
    const predictionLabel = document.getElementById('predictionLabel');
    if (predictionLabel) {
        predictionLabel.textContent = `Error: ${error}`;
        predictionLabel.className = 'text-danger';
    }
}

function loadStatistics() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading stats:', data.error);
                return;
            }
            
            updateStatisticsDashboard(data);
            updateQuickStats(data);
        })
        .catch(error => {
            console.error('Error loading statistics:', error);
        });
}

function updateStatisticsDashboard(data) {
    const elements = {
        totalProducts: document.getElementById('totalProducts'),
        totalReviews: document.getElementById('totalReviews'),
        avgRating: document.getElementById('avgRating'),
        categories: document.getElementById('categories')
    };
    
    if (elements.totalProducts) {
        elements.totalProducts.textContent = data.total_products || 0;
    }
    
    if (elements.totalReviews) {
        elements.totalReviews.textContent = data.total_reviews || 0;
    }
    
    if (elements.avgRating) {
        const avgRating = calculateAverageRating(data.rating_distribution);
        elements.avgRating.textContent = avgRating;
    }
    
    if (elements.categories) {
        elements.categories.textContent = data.categories ? data.categories.length : 0;
    }
}

function calculateAverageRating(ratingDistribution) {
    if (!ratingDistribution || ratingDistribution.length === 0) return '0.0';
    
    let totalRating = 0;
    let totalCount = 0;
    
    ratingDistribution.forEach(item => {
        totalRating += item._id * item.count;
        totalCount += item.count;
    });
    
    return totalCount > 0 ? (totalRating / totalCount).toFixed(1) : '0.0';
}

function updateQuickStats(data) {
    const quickStatsDiv = document.getElementById('quickStats');
    if (!quickStatsDiv) return;
    
    if (data.categories && data.categories.length > 0) {
        const topCategories = data.categories.slice(0, 3);
        let html = '<h6>Top Categories:</h6>';
        
        topCategories.forEach(cat => {
            html += `
                <div class="d-flex justify-content-between mb-1">
                    <small>${cat._id}</small>
                    <small class="text-muted">${cat.count}</small>
                </div>
            `;
        });
        
        quickStatsDiv.innerHTML = html;
    } else {
        quickStatsDiv.innerHTML = '<p class="text-muted mb-0">No data available</p>';
    }
}

function showLoadingState() {
    const loadingElements = document.querySelectorAll('[data-loading]');
    loadingElements.forEach(element => {
        element.classList.add('loading');
    });
}

function hideLoadingState() {
    const loadingElements = document.querySelectorAll('[data-loading]');
    loadingElements.forEach(element => {
        element.classList.remove('loading');
    });
}

function showFormErrors(form) {
    const invalidElements = form.querySelectorAll(':invalid');
    invalidElements.forEach(element => {
        element.classList.add('is-invalid');
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
        }, 5000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Load saved preferences
function loadPreferences() {
    const viewPreference = localStorage.getItem('viewPreference');
    if (viewPreference === 'list') {
        switchToListView();
    } else {
        switchToGridView();
    }
}

// Initialize preferences on load
document.addEventListener('DOMContentLoaded', loadPreferences);

// Export functions for global use
window.FashionStore = {
    predictReview,
    updatePredictionDisplay,
    showNotification,
    switchToGridView,
    switchToListView
};