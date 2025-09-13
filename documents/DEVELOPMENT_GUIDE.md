# 🔄 Development Guide - File Synchronization

This guide explains how to work with the Fashion Store application in both development and production modes.

## [START] Quick Start

### For Development (Live File Sync)
```bash
./dev.sh
```
- **What it does**: Starts the app with live file synchronization
- **Best for**: When you're actively coding and want changes to appear immediately
- **Files synced**: `app.py`, `templates/`, `static/`, `ml_utils.py`

### For Production (Lecturer Testing)
```bash
./prod.sh
```
- **What it does**: Starts the app in production mode
- **Best for**: When your lecturer wants to test the final version
- **Files**: All code is built into the Docker image

## 📁 File Synchronization Methods

### Method 1: Docker Volumes (Recommended)
The development mode uses Docker volumes to automatically sync files:

```yaml
volumes:
  - ./app.py:/app/app.py                    # Python files
  - ./templates:/app/templates              # HTML templates
  - ./static:/app/static                    # CSS/JS/images
  - ./ml_utils.py:/app/ml_utils.py         # ML utilities
```

**Advantages:**
- [SUCCESS] Automatic sync - no manual copying needed
- [SUCCESS] Real-time updates
- [SUCCESS] Works on any operating system
- [SUCCESS] No performance impact

### Method 2: Manual Copy (Backup Method)
If volumes don't work, you can still copy files manually:

```bash
# Copy specific files
docker cp app.py fashion_store_web:/app/
docker cp templates/ fashion_store_web:/app/
docker cp static/ fashion_store_web:/app/

# Copy everything at once
docker cp . fashion_store_web:/app/ --exclude=node_modules --exclude=.git
```

##  Development Workflow

### 1. Start Development Mode
```bash
./dev.sh
```

### 2. Make Changes
Edit any file in your local directory:
- `app.py` - Flask routes and logic
- `templates/*.html` - HTML templates
- `static/css/style.css` - Styling
- `static/js/main.js` - JavaScript

### 3. See Changes Instantly
- Changes appear immediately in the browser
- No need to restart the container
- Flask auto-reloads Python files

### 4. Test Your Changes
- Visit `http://localhost:6600`
- Login with: `test@example.com` / `test123`
- Test all features: profile, wishlist, product details

## [TARGET] For Your Lecturer

### Production Setup
When your lecturer wants to test:

1. **Give them the production script:**
   ```bash
   ./prod.sh
   ```

2. **Or use Docker Compose directly:**
   ```bash
   docker-compose up --build -d
   ```

3. **Application will be available at:**
   - URL: `http://localhost:6600`
   - Demo login: `test@example.com` / `test123`

### What's Included in Production
- [SUCCESS] All your code changes
- [SUCCESS] Pre-trained ML models
- [SUCCESS] Product data and images
- [SUCCESS] User accounts and reviews
- [SUCCESS] All UI/UX enhancements

## [PROCESS] Troubleshooting

### If Files Don't Sync
1. **Check if development mode is running:**
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```

2. **Restart development mode:**
   ```bash
   ./dev.sh
   ```

3. **Check volume mounts:**
   ```bash
   docker inspect fashion_store_web | grep -A 10 "Mounts"
   ```

### If Changes Don't Appear
1. **Check Flask logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs web
   ```

2. **Force refresh browser** (Ctrl+F5 or Cmd+Shift+R)

3. **Check file permissions:**
   ```bash
   ls -la app.py templates/ static/
   ```

##  File Structure

```
asm3-online-shopping/
├── app.py                    # Main Flask application
├── ml_utils.py              # ML model utilities
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── profile.html
│   ├── wishlist.html
│   └── product_detail.html
├── static/                  # Static assets
│   ├── css/style.css
│   └── js/main.js
├── docker-compose.yml       # Production configuration
├── docker-compose.dev.yml   # Development configuration
├── dev.sh                   # Development startup script
├── prod.sh                  # Production startup script
└── README.md
```

## [COMPLETE] Benefits

### For You (Development)
- ⚡ **Instant feedback** - see changes immediately
- 🔄 **No manual copying** - files sync automatically
- 🐛 **Easy debugging** - logs show in real-time
-  **Familiar workflow** - edit files locally

### For Your Lecturer (Production)
- 📦 **Self-contained** - everything built into the image
- [START] **Easy to run** - just one command
-  **Production-ready** - optimized and secure
- [DATA] **Complete features** - all functionality included

## 🚨 Important Notes

1. **Always use development mode** when coding
2. **Switch to production mode** only for final testing
3. **Commit your changes** to git before switching modes
4. **Test thoroughly** in production mode before submission

---

**Happy coding! [COMPLETE]** Your lecturer will be impressed with the smooth development workflow and professional production setup.
