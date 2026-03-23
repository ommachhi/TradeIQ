# TradeIQ API Documentation

## Overview

The TradeIQ API provides endpoints for stock price prediction and historical data retrieval. The API is built with Django REST Framework and uses JSON for all requests and responses.

## Base URL

```
http://localhost:8000/api
```

## Headers

All requests should include:

```
Content-Type: application/json
```

## Response Format

All responses are JSON-formatted and include appropriate HTTP status codes.

### Success Response (200 OK)
```json
{
  "data": "success"
}
```

### Error Response (4xx/5xx)
```json
{
  "error": "Error message",
  "details": "Additional details"
}
```

---

## Endpoints

### 1. Health Check

Check if the API is running and model is loaded.

**Endpoint**:
```
GET /api/health/
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "message": "TradeIQ API is running",
  "model_loaded": true,
  "timestamp": "2024-01-23T12:00:00.000000"
}
```

**Status Codes**:
- `200` - API is healthy
- `503` - API unavailable

**Example**:
```bash
curl http://localhost:8000/api/health/
```

---

### 2. Stock Price Prediction

Predict the closing price of a stock based on market data.

**Endpoint**:
```
POST /api/predict/
```

**Request Body**:
```json
{
  "open": 120.5,
  "high": 125.0,
  "low": 118.2,
  "volume": 450000
}
```

**Parameters**:
| Parameter | Type | Required | Min Value | Description |
|-----------|------|----------|-----------|-------------|
| open | float | Yes | 0 | Opening price |
| high | float | Yes | 0 | Highest price of the day |
| low | float | Yes | 0 | Lowest price of the day |
| volume | integer | Yes | 0 | Trading volume in shares |

**Validation Rules**:
- `high >= low`
- `low <= open <= high`
- All values must be positive numbers

**Response** (200 OK):
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

**Recommendation Logic**:
```
if predicted_price > open_price:
    recommendation = "BUY"
elif predicted_price < open_price:
    recommendation = "SELL"
else:
    recommendation = "HOLD"
```

**Status Codes**:
- `200` - Prediction successful
- `400` - Invalid input data
- `503` - Model not available

**Error Response** (400 Bad Request):
```json
{
  "error": "Invalid input data",
  "details": {
    "open": ["This field is required."],
    "high": ["Ensure this value is greater than or equal to low price."]
  }
}
```

**Examples**:

```bash
# Using curl
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "open": 120.5,
    "high": 125.0,
    "low": 118.2,
    "volume": 450000
  }'

# Using Python requests
import requests

data = {
    "open": 120.5,
    "high": 125.0,
    "low": 118.2,
    "volume": 450000
}

response = requests.post(
    'http://localhost:8000/api/predict/',
    json=data
)

prediction = response.json()
print(f"Predicted Price: ${prediction['predicted_price']}")
print(f"Recommendation: {prediction['recommendation']}")
```

---

### 3. Historical Data

Get historical stock price data.

**Endpoint**:
```
GET /api/history/
```

**Query Parameters** (optional):
| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Limit number of records (e.g., ?limit=30) |
| offset | integer | Offset for pagination (e.g., ?offset=10) |

**Response** (200 OK):
```json
[
  {
    "date": "2023-01-01",
    "open": 100.36,
    "high": 101.24,
    "low": 100.12,
    "close": 100.45,
    "volume": 4070321
  },
  {
    "date": "2023-01-02",
    "open": 100.39,
    "high": 101.01,
    "low": 99.55,
    "close": 100.34,
    "volume": 3890978
  }
]
```

**Data Fields**:
| Field | Type | Description |
|-------|------|-------------|
| date | string (YYYY-MM-DD) | Trading date |
| open | float | Opening price |
| high | float | Highest price of the day |
| low | float | Lowest price of the day |
| close | float | Closing price |
| volume | integer | Trading volume |

**Status Codes**:
- `200` - Data retrieved successfully
- `404` - CSV file not found
- `400` - CSV parsing error
- `500` - Server error

**Examples**:

```bash
# Get all historical data
curl http://localhost:8000/api/history/

# Get limited data
curl http://localhost:8000/api/history/?limit=30

# Using Python
import requests

response = requests.get('http://localhost:8000/api/history/')
history = response.json()

for record in history:
    print(f"{record['date']}: ${record['close']} ({record['volume']} shares)")
```

---

## Status Codes Reference

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | API/Model not available |

---

## Error Handling

### Common Error Scenarios

**Invalid Input Type**:
```json
{
  "error": "Invalid input data",
  "details": {
    "open": ["A valid number is required."]
  }
}
```

**Missing Required Fields**:
```json
{
  "error": "Invalid input data",
  "details": {
    "volume": ["This field is required."]
  }
}
```

**Invalid Price Logic**:
```json
{
  "error": "Invalid input data",
  "details": {
    "non_field_errors": [
      "High price must be greater than or equal to low price"
    ]
  }
}
```

**Model Not Available**:
```json
{
  "error": "ML Model not available",
  "message": "The prediction model could not be loaded. Please ensure model.pkl exists."
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider implementing:
- Requests per second per IP
- Requests per day per API key
- Token-based rate limiting

---

## Authentication

Currently no authentication is required. All endpoints are publicly accessible.

For production, implement:
- API Key authentication
- JWT token authentication
- OAuth 2.0

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:5173` (React dev server)
- `http://localhost:3000` (Alternative frontend port)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

For production, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

---

## Performance Considerations

- Average response time: < 100ms
- Model inference time: ~10-50ms
- CSV loading time: ~500-1000ms (on first request)

---

## Testing the API

### Using Postman

1. Create a POST request to `http://localhost:8000/api/predict/`
2. Set Content-Type to `application/json`
3. Add body:
```json
{
  "open": 120.5,
  "high": 125.0,
  "low": 118.2,
  "volume": 450000
}
```
4. Click Send

### Using Python

```python
import requests

# Health check
response = requests.get('http://localhost:8000/api/health/')
print(response.json())

# Get prediction
data = {
    "open": 120.5,
    "high": 125.0,
    "low": 118.2,
    "volume": 450000
}
response = requests.post('http://localhost:8000/api/predict/', json=data)
print(response.json())

# Get history
response = requests.get('http://localhost:8000/api/history/')
history = response.json()
print(f"Total records: {len(history)}")
```

### Using JavaScript/Fetch

```javascript
// Health check
fetch('http://localhost:8000/api/health/')
  .then(response => response.json())
  .then(data => console.log(data));

// Get prediction
const data = {
  open: 120.5,
  high: 125.0,
  low: 118.2,
  volume: 450000
};

fetch('http://localhost:8000/api/predict/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Changelog

### Version 1.0.0 (2024-01-23)
- Initial release
- Prediction endpoint
- History endpoint
- Health check endpoint

---

## Support

For API issues:
1. Check server is running: `http://localhost:8000`
2. Verify model is loaded: `GET /api/health/`
3. Check request format and parameters
4. Review error messages
5. Check Django logs for detailed errors

---

**Last Updated**: January 2024
