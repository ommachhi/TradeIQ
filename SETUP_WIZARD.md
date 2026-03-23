"""
TradeIQ - Stock Market Prediction Application
Complete Setup and Run Guide

╔══════════════════════════════════════════════════════════════════════════════╗
║                          TRADEIQ SETUP WIZARD                               ║
║                      Stock Market Prediction System                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
1️⃣  PREREQUISITES CHECK
═══════════════════════════════════════════════════════════════════════════════

Before starting, verify you have:

✓ Python 3.8+
  Command: python --version
  Expected: Python 3.x.x

✓ Node.js 16+
  Command: node --version
  Expected: v16.x.x or higher

✓ npm 7+
  Command: npm --version
  Expected: 7.x.x or higher

═══════════════════════════════════════════════════════════════════════════════
2️⃣  PROJECT STRUCTURE VERIFICATION
═══════════════════════════════════════════════════════════════════════════════

Check that these directories exist:
  ✓ TredalQ/
  ✓ TredalQ/Datasets/
  ✓ TredalQ/tradeiq_backend/
  ✓ TredalQ/tradeiq_frontend/

Essential files present:
  ✓ TredalQ/train_model.py
  ✓ TredalQ/tradeiq_backend/manage.py
  ✓ TredalQ/tradeiq_backend/requirements.txt
  ✓ TredalQ/tradeiq_frontend/package.json
  ✓ TredalQ/Datasets/TradeIQ_stock_data.csv

═══════════════════════════════════════════════════════════════════════════════
3️⃣  INSTALLATION STEPS
═══════════════════════════════════════════════════════════════════════════════

STEP 3.1: Create Virtual Environment
────────────────────────────────────────

Windows:
  > cd TredalQ
  > python -m venv .venv
  > .venv\Scripts\activate
  (You should see (.venv) in your prompt)

Mac/Linux:
  $ cd TredalQ
  $ python3 -m venv .venv
  $ source .venv/bin/activate
  (You should see (.venv) in your prompt)


STEP 3.2: Install Backend Dependencies
────────────────────────────────────────

Make sure virtual environment is activated:

  > pip install -r tradeiq_backend/requirements.txt

Expected packages installed:
  ✓ Django 4.2.8
  ✓ djangorestframework 3.14.0
  ✓ django-cors-headers 4.3.1
  ✓ pandas 2.1.4
  ✓ scikit-learn 1.3.2
  ✓ numpy 1.26.3


STEP 3.3: Train ML Model
────────────────────────

  > python train_model.py

Expected output:
  Dataset shape: (1565, 6)
  Training data shape: (1565, 4)
  Model Performance:
  Training R² Score: 0.9999
  Testing R² Score: 0.9997
  ✓ Model saved successfully as 'tradeiq_backend/model.pkl'


STEP 3.4: Install Frontend Dependencies
────────────────────────────────────────

In a NEW terminal (do NOT use Python venv for this):

  > cd TredalQ
  > cd tradeiq_frontend
  > npm install

Expected output:
  ...
  added 150 packages in XX.XXs


STEP 3.5: Verify Installation
──────────────────────────────

Backend verification:
  > cd TredalQ/tradeiq_backend
  > python manage.py check

Expected output:
  System check identified no issues (0 silenced).


Frontend verification:
  > cd TredalQ/tradeiq_frontend
  > npm --version

Expected output:
  7.x.x or higher

═══════════════════════════════════════════════════════════════════════════════
4️⃣  STARTING THE APPLICATION
═══════════════════════════════════════════════════════════════════════════════

OPTION A: Manual Startup (Recommended for Development)
─────────────────────────────────────────────────────

Terminal 1 - Django Backend:
  1. Open command prompt/terminal
  2. cd TredalQ
  3. .venv\Scripts\activate  (Windows) or source .venv/bin/activate (Mac/Linux)
  4. cd tradeiq_backend
  5. python manage.py runserver
  
  Expected:
    Watching for file changes with StatReloader
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CTRL-BREAK.


Terminal 2 - React Frontend:
  1. Open NEW command prompt/terminal
  2. cd TredalQ
  3. cd tradeiq_frontend
  4. npm run dev
  
  Expected:
    ➜  Local:   http://localhost:5173/
    ➜  press h to show help


OPTION B: Automated Startup (One Command)
──────────────────────────────────────────

Windows:
  > cd TredalQ
  > run_servers.bat

Mac/Linux:
  $ cd TredalQ
  $ chmod +x run_servers.sh
  $ ./run_servers.sh

Both servers will start in separate windows.

═══════════════════════════════════════════════════════════════════════════════
5️⃣  ACCESS THE APPLICATION
═══════════════════════════════════════════════════════════════════════════════

Open your browser and go to:

  🌐 http://localhost:5173

You should see:
  ✓ TradeIQ logo and title
  ✓ Navigation menu (Home, Predict, Analysis)
  ✓ Green "API: Connected" status indicator
  ✓ Feature cards
  ✓ Call-to-action buttons

═══════════════════════════════════════════════════════════════════════════════
6️⃣  TEST THE APPLICATION
═══════════════════════════════════════════════════════════════════════════════

TEST 1: API Health Check
────────────────────────

Open browser console or terminal:
  curl http://localhost:8000/api/health/

Expected:
  {
    "status": "healthy",
    "message": "TradeIQ API is running",
    "model_loaded": true,
    "timestamp": "..."
  }


TEST 2: Make a Prediction
─────────────────────────

1. Click "Predict" in navigation
2. Fill in values:
   - Opening Price: 120.5
   - Highest Price: 125.0
   - Lowest Price: 118.2
   - Trading Volume: 450000
3. Click "Get Prediction"

Expected:
  ✓ Predicted Price: $123.40 (or similar)
  ✓ Recommendation: BUY/SELL/HOLD badge
  ✓ Input summary displayed


TEST 3: View Historical Data
────────────────────────────

1. Click "Analysis" in navigation
2. Wait for chart to load (should take <2 seconds)

Expected:
  ✓ Line chart showing 60 days of data
  ✓ Statistics cards (Latest Close, Highest, Lowest, Data Points)
  ✓ Market insights section


TEST 4: Navigate Pages
──────────────────────

✓ Click "Home" - See landing page
✓ Click "Predict" - See prediction form
✓ Click "Analysis" - See charts
✓ All pages load quickly
✓ Navigation is smooth

═══════════════════════════════════════════════════════════════════════════════
7️⃣  TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

❌ "API: Disconnected" on Home Page
✓ Ensure Django is running on port 8000
✓ Check Terminal 1 for errors
✓ Try: curl http://localhost:8000/api/health/

❌ "Cannot find module" errors
✓ Ensure virtual environment is activated
✓ Run: pip install -r tradeiq_backend/requirements.txt
✓ Make sure you're in the correct directory

❌ npm install fails
✓ Try: npm cache clean --force
✓ Delete node_modules and package-lock.json
✓ Run: npm install again

❌ Port already in use (8000 or 5173)
✓ Windows: netstat -ano | findstr :8000
✓ Mac/Linux: lsof -i :8000
✓ Kill the process: taskkill /PID <PID> /F

❌ Model not loading
✓ Verify model.pkl exists: ls tradeiq_backend/model.pkl
✓ If missing, retrain: python train_model.py
✓ Check file permissions

═══════════════════════════════════════════════════════════════════════════════
8️⃣  IMPORTANT PORTS
═══════════════════════════════════════════════════════════════════════════════

Frontend:  http://localhost:5173  (React Vite Dev Server)
Backend:   http://localhost:8000  (Django Development Server)
API:       http://localhost:8000/api/ (REST API Endpoints)

If ports are blocked, check:
  - Firewall settings
  - Other applications using the ports
  - Port forwarding if on virtual machine

═══════════════════════════════════════════════════════════════════════════════
9️⃣  STOPPING THE APPLICATION
═══════════════════════════════════════════════════════════════════════════════

Terminal 1 (Backend):
  Press Ctrl+C
  Message: KeyboardInterrupt

Terminal 2 (Frontend):
  Press Ctrl+C
  Message: Any key to exit

═══════════════════════════════════════════════════════════════════════════════
🔟 HELPFUL COMMANDS REFERENCE
═══════════════════════════════════════════════════════════════════════════════

Python/Django:
  python manage.py runserver          # Start Django server
  python manage.py migrate            # Apply migrations
  python manage.py shell              # Django Python shell
  python manage.py check              # Check configuration
  python train_model.py               # Train ML model

Node/React:
  npm install                         # Install dependencies
  npm run dev                         # Start dev server
  npm run build                       # Build for production
  npm run preview                     # Preview production build
  npm cache clean --force             # Clear npm cache

Virtual Environment:
  python -m venv .venv                # Create venv
  .venv\Scripts\activate              # Activate (Windows)
  source .venv/bin/activate           # Activate (Mac/Linux)
  deactivate                          # Deactivate venv

═══════════════════════════════════════════════════════════════════════════════
📚 DOCUMENTATION FILES
═══════════════════════════════════════════════════════════════════════════════

README.md              → Complete project documentation
QUICK_START.md         → Fast setup guide (this file)
INSTALLATION.md        → Detailed installation steps
API_DOCUMENTATION.md   → Full API reference
PROJECT_SUMMARY.md     → Project completion summary

═══════════════════════════════════════════════════════════════════════════════
✅ SUCCESS CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

After completing all steps, verify:

  ✓ Backend running at http://localhost:8000
  ✓ Frontend running at http://localhost:5173
  ✓ API health check returns "healthy"
  ✓ Home page shows "API: Connected"
  ✓ Can navigate between all pages
  ✓ Prediction form accepts input
  ✓ Prediction returns results
  ✓ Analysis page shows chart
  ✓ Historical data is displayed
  ✓ No console errors in browser
  ✓ No errors in terminals

═══════════════════════════════════════════════════════════════════════════════
🎉 YOU'RE ALL SET!
═══════════════════════════════════════════════════════════════════════════════

Your TradeIQ application is now running and ready to use!

For detailed information, visit:
  - README.md for complete guide
  - API_DOCUMENTATION.md for API details
  - INSTALLATION.md for troubleshooting

Happy trading! 📈

═══════════════════════════════════════════════════════════════════════════════
"""
