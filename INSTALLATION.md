# TradeIQ - Complete Installation & Testing Guide

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 2GB minimum
- **Disk Space**: 500MB
- **Internet**: Required for npm package downloads

## Software Requirements

### Required
- Python 3.8 or higher
- Node.js 16.0 or higher
- npm 7.0 or higher

### Verification

Check your versions:

```bash
python --version
node --version
npm --version
```

## Full Installation Steps

### 1. Environment Setup (First Time Only)

#### Windows Users

```bash
# Navigate to project directory
cd TredalQ

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# You should see (.venv) in your terminal prompt
```

#### Mac/Linux Users

```bash
# Navigate to project directory
cd TredalQ

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

### 2. Backend Setup

```bash
# Ensure virtual environment is activated
# (You should see (.venv) in terminal)

# Install backend dependencies
pip install -r tradeiq_backend/requirements.txt

# Navigate to backend
cd tradeiq_backend

# Run the Django development server
python manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **Backend is now running!**

### 3. Frontend Setup (New Terminal Window)

```bash
# DO NOT activate venv for this terminal
# This uses Node.js/npm, not Python

# Navigate to project directory
cd TredalQ

# Navigate to frontend
cd tradeiq_frontend

# Install frontend dependencies
npm install

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

✅ **Frontend is now running!**

### 4. Access the Application

Open your browser and go to:

```
http://localhost:5173
```

You should see:
- TradeIQ logo and branding
- Three navigation links: Home, Predict, Analysis
- Green "API: Connected" status indicator
- Call-to-action buttons

## Automated Startup

### Windows

```bash
# Run batch file to start both servers
run_servers.bat
```

This will open 2 new command windows and start both servers.

### Mac/Linux

```bash
# Make script executable
chmod +x run_servers.sh

# Run script
./run_servers.sh
```

## Manual Server Startup

If automated startup doesn't work:

### Terminal 1: Backend

```bash
cd TredalQ
.venv\Scripts\activate  # or: source .venv/bin/activate
cd tradeiq_backend
python manage.py runserver
```

Wait for: "Starting development server at http://127.0.0.1:8000/"

### Terminal 2: Frontend

```bash
cd TredalQ
cd tradeiq_frontend
npm run dev
```

Wait for: "Local: http://localhost:5173/"

## Testing the Application

### Test 1: API Health Check

```bash
# Open any terminal and run:
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "TradeIQ API is running",
  "model_loaded": true,
  "timestamp": "2024-01-23T12:00:00.000000"
}
```

### Test 2: Get Historical Data

```bash
curl http://localhost:8000/api/history/
```

Should return an array of stock data with dates, prices, and volumes.

### Test 3: Make a Prediction

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"open": 120.5, "high": 125.0, "low": 118.2, "volume": 450000}'
```

Expected response:
```json
{
  "predicted_price": 123.4,
  "recommendation": "BUY",
  "input": {
    "open": 120.5,
    "high": 125.0,
    "low": 118.2,
    "volume": 450000
  }
}
```

### Test 4: UI Testing

1. **Home Page**
   - [ ] Logo and title display correctly
   - [ ] "API: Connected" shows green status
   - [ ] Feature cards are visible
   - [ ] Tech stack section displays
   - [ ] Buttons are clickable

2. **Predict Page**
   - [ ] Form loads with 4 input fields
   - [ ] Can enter values
   - [ ] Submit button works
   - [ ] Prediction displays with badge
   - [ ] Error messages show for invalid input

3. **Analysis Page**
   - [ ] Chart loads and displays data
   - [ ] Statistics cards show values
   - [ ] Chart is interactive (hover tooltip works)
   - [ ] Data loads correctly

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'django'"

**Solution**:
```bash
# Ensure virtual environment is activated (.venv in prompt)
pip install -r tradeiq_backend/requirements.txt
```

### Issue 2: "command not found: npm"

**Solution**:
- Download Node.js from https://nodejs.org (includes npm)
- Restart your terminal
- Verify: `npm --version`

### Issue 3: Port 8000 already in use

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### Issue 4: "Cannot find module" in React

**Solution**:
```bash
cd tradeiq_frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue 5: "CSV file not found"

**Solution**:
- Check that `TradeIQ_stock_data.csv` exists in `tradeiq_backend/`
- Also in `Datasets/` directory
- File is copied automatically during installation

### Issue 6: Model not loading

**Solution**:
```bash
# Retrain the model
python train_model.py

# Should output:
# Model Performance:
# Training R² Score: 0.9999
# Testing R² Score: 0.9997
# ✓ Model saved successfully as 'tradeiq_backend/model.pkl'
```

### Issue 7: CORS errors in browser console

**Solution**:
- Ensure backend is running on port 8000
- Check `CORS_ALLOWED_ORIGINS` in `settings.py`
- Restart both servers

## Development Workflow

### Making Changes

**Backend Changes**:
1. Modify Python files in `tradeiq_backend/`
2. Django auto-reloads on file save
3. Test via API endpoints

**Frontend Changes**:
1. Modify React files in `tradeiq_frontend/src/`
2. Vite auto-updates in browser
3. Check browser for immediate results

### Running Linters/Formatters

**Python**:
```bash
# Install linter (optional)
pip install flake8

# Check code
flake8 tradeiq_backend/
```

**JavaScript**:
```bash
# Install ESLint (optional)
npm install --save-dev eslint

# Check code
npx eslint src/
```

## Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Update `SECRET_KEY` in settings.py
- [ ] Update `ALLOWED_HOSTS` in settings.py
- [ ] Update `CORS_ALLOWED_ORIGINS` for your domain
- [ ] Use proper database (PostgreSQL, MySQL)
- [ ] Use proper WSGI server (Gunicorn)
- [ ] Set up SSL/HTTPS
- [ ] Configure environment variables
- [ ] Set up static/media file serving
- [ ] Configure logging
- [ ] Run security checks: `python manage.py check --deploy`

## Stopping the Application

### Kill Both Servers

Press `Ctrl+C` in each terminal window where the servers are running.

Or if using `run_servers.bat/sh`, close the terminal windows.

## Next Steps

1. ✅ Application is running
2. Test all features according to "Testing" section
3. Review code in `tradeiq_backend/` and `tradeiq_frontend/`
4. Make any customizations needed
5. Deploy to production when ready

## File Structure Reference

```
TredalQ/
├── .venv/                  # Virtual environment
├── Datasets/
│   └── TradeIQ_stock_data.csv
├── tradeiq_backend/
│   ├── tradeiq_backend/    # Django project settings
│   ├── prediction/         # API application
│   ├── model.pkl           # ML model
│   ├── manage.py
│   └── requirements.txt
├── tradeiq_frontend/
│   ├── src/                # React source code
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── train_model.py          # Model training script
├── README.md               # Full documentation
├── QUICK_START.md          # Quick setup guide
└── INSTALLATION.md         # This file
```

## Support

If you encounter issues:

1. Check this guide's "Common Issues" section
2. Check the main README.md for detailed information
3. Review terminal error messages carefully
4. Verify all prerequisites are installed
5. Ensure both servers are running on correct ports

---

**Ready to run TradeIQ? Start with Step 1! 🚀**
