# TradeIQ - Quick Setup Guide

## 🚀 Quick Start (2 Steps)

### Prerequisites Check
- Python 3.8+
- Node.js 16+
- npm 7+

### Step 1: Setup Backend (2 minutes)

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Mac/Linux

# Install Python packages (if not done)
pip install -r tradeiq_backend/requirements.txt

# Train ML model (if not done)
python train_model.py

# Navigate to backend
cd tradeiq_backend

# Start Django server
python manage.py runserver
```

The backend will start at: **http://localhost:8000**

Terminal output should show:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 2: Setup Frontend (2 minutes)

In a **NEW terminal window**:

```bash
# Navigate to frontend
cd tradeiq_frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

The frontend will start at: **http://localhost:5173**

Terminal output should show:
```
➜  Local:   http://localhost:5173/
```

### Open in Browser

```
http://localhost:5173
```

## ✅ Verification Checklist

After starting both servers, verify:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Home page shows "API: Connected" status
- [ ] Can navigate to all 3 pages (Home, Predict, Analysis)
- [ ] Prediction form loads without errors
- [ ] Historical chart displays data

## 📱 Testing the Application

### Test 1: Prediction
1. Go to **Predict** page
2. Enter values:
   - Open: 120.5
   - High: 125.0
   - Low: 118.2
   - Volume: 450000
3. Click "Get Prediction"
4. Should show predicted price and recommendation

### Test 2: Analysis
1. Go to **Analysis** page
2. Should display historical price chart
3. Chart should show 60 days of data
4. Statistics should display: Latest Close, Highest, Lowest, Data Points

## 🆘 Troubleshooting

### "Cannot connect to backend"
```bash
# Verify backend is running
curl http://localhost:8000/api/health/
```

### "Module not found" errors
```bash
pip install --upgrade pip
pip install -r tradeiq_backend/requirements.txt
```

### "npm module not found"
```bash
cd tradeiq_frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

## 🎯 Common Commands

```bash
# Backend
cd tradeiq_backend
python manage.py migrate         # Run migrations
python manage.py runserver       # Start server
python manage.py shell          # Django shell

# Frontend
cd tradeiq_frontend
npm run dev                      # Start dev server
npm run build                    # Build for production
npm run preview                  # Preview production build
```

## 📊 API Testing

Test the API directly using curl:

```bash
# Health check
curl http://localhost:8000/api/health/

# Get historical data
curl http://localhost:8000/api/history/

# Make prediction
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"open": 120.5, "high": 125.0, "low": 118.2, "volume": 450000}'
```

## 📁 Project Structure at a Glance

```
TradeIQ/
├── tradeiq_backend/          ← Django Backend
│   ├── prediction/           ← API views, models, serializers
│   ├── model.pkl             ← Trained ML model
│   ├── manage.py
│   └── requirements.txt
├── tradeiq_frontend/         ← React Frontend
│   ├── src/
│   │   ├── components/       ← Reusable components
│   │   ├── pages/            ← Page components
│   │   ├── services/         ← API client (api.js)
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── Datasets/
│   └── TradeIQ_stock_data.csv
├── train_model.py            ← ML model training script
└── README.md
```

## 🎓 For College Submission

This project is ready for submission with:

✅ Complete backend with ML integration
✅ Full-featured React frontend
✅ Responsive design with Tailwind CSS
✅ Comprehensive documentation
✅ Working examples and test data
✅ Error handling throughout
✅ Code comments and docstrings
✅ Clean architecture

## 📞 Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Frontend | http://localhost:5173 | 5173 |
| Backend | http://localhost:8000 | 8000 |
| API | http://localhost:8000/api | 8000 |

## ⏱️ Typical Startup Time

- Backend: ~2 seconds
- Frontend: ~5 seconds
- Total: ~7 seconds to fully ready

---

**Ready to predict stock prices? Start with Step 1! 🚀**
