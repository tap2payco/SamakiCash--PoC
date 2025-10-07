# SamakiCash Frontend Integration Guide 🚀

## For Frontend Developers

This guide provides everything your frontend team needs to integrate with the SamakiCash backend API.

---

## 🔗 **API Base URL**

### Development
```
http://localhost:8000
```

### Production (Render)
```
https://samakicash.onrender.com
```

---

## 📋 **API Endpoints Reference**

### 1. **Authentication**

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "user_type": "fisher",  // "fisher", "seller", or "buyer"
  "name": "John Doe",
  "phone": "+255123456789",
  "organization": "Lake Victoria Fisheries",  // optional
  "location": "Mwanza, Tanzania"  // optional
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "uuid-string",
  "user_type": "fisher"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "user_id": "uuid-string",
  "user_type": "fisher",
  "message": "Login successful"
}
```

---

### 2. **Fish Catch Analysis**

#### Analyze Catch
```http
POST /api/analyze-catch
Content-Type: application/json

{
  "fish_type": "tilapia",
  "quantity_kg": 15.5,
  "location": "Mwanza",
  "user_id": "user-uuid",
  "image_data": "base64-encoded-image"  // optional
}
```

**Response:**
```json
{
  "status": "success",
  "price_analysis": {
    "fair_price": 5200,
    "currency": "TZS",
    "reasoning": "High demand in Mwanza market",
    "confidence_score": 0.8
  },
  "market_insights": {
    "market_trend": "Growing demand",
    "competitor_analysis": "Average price: 4000-6000 TZS/kg",
    "recommendation": "Sell in morning for best prices"
  },
  "image_analysis": {
    "quality_assessment": "good",
    "freshness": "fresh",
    "confidence": 0.7
  },
  "voice_message_url": "/audio/price_alert_abc123.mp3",  // or null
  "analysis_summary": "15.5 kg of tilapia in Mwanza. Suggested price: 5200 TZS/kg. Market trend: Growing demand.",
  "recommendation": "Suggested price: TZS 5200 per kg"
}
```

---

### 3. **Matchmaking**

#### Find Buyer Matches
```http
POST /api/match
Content-Type: application/json

{
  "fish_type": "tilapia",
  "quantity_kg": 15.5,
  "location": "Mwanza",
  "user_id": "user-uuid"  // optional
}
```

**Response:**
```json
{
  "status": "success",
  "matches": [
    {
      "buyer_id": "buyer-uuid",
      "buyer_contact": "buyer@example.com",
      "buyer_name": "Lake Hotel",
      "buyer_organization": "Lake Victoria Hotels",
      "buyer_location": "Mwanza",
      "match_score": 85,
      "estimated_price_per_kg": 5200,
      "estimated_total_value": 80600,
      "reason": "High demand for tilapia in Mwanza area",
      "note": "Simulated match (use buyer preferences in production)"
    }
  ],
  "price_analysis": { /* same as analyze-catch */ },
  "market_insights": { /* same as analyze-catch */ },
  "analysis_summary": "15.5 kg of tilapia at Mwanza. Suggested price: 5200 TZS/kg. Market trend: Growing demand."
}
```

---

### 4. **Financial Services**

#### Get Credit Score
```http
POST /api/credit-score
Content-Type: application/json

"user-uuid"  // Send as raw string in body
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "credit_score": 750,
  "loan_eligible": true,
  "max_loan_amount": 750000,
  "catch_count": 12,
  "score_components": {
    "base_score": 650,
    "activity_bonus": 100,
    "total_catches": 12
  }
}
```

#### Apply for Loan
```http
POST /api/loan-application
Content-Type: application/json

{
  "user_id": "user-uuid",
  "amount": 500000,
  "purpose": "fishing_equipment"
}
```

**Response:**
```json
{
  "status": "approved",
  "user_id": "user-uuid",
  "amount": 500000,
  "purpose": "fishing_equipment",
  "credit_score": 750,
  "message": "Loan application approved"
}
```

#### Get Insurance Quote
```http
POST /api/insurance-quote
Content-Type: application/json

{
  "user_id": "user-uuid",
  "coverage_type": "equipment",
  "coverage_amount": 1000000
}
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "coverage_type": "equipment",
  "coverage_amount": 1000000,
  "annual_premium": 50000,
  "message": "Comprehensive coverage"
}
```

---

### 5. **User Management**

#### List Buyers
```http
GET /api/users/buyers
```

**Response:**
```json
{
  "count": 5,
  "buyers": [
    {
      "id": "buyer-uuid",
      "email": "buyer@example.com",
      "user_type": "buyer",
      "name": "Lake Hotel",
      "organization": "Lake Victoria Hotels",
      "location": "Mwanza"
    }
  ]
}
```

#### List Sellers
```http
GET /api/users/sellers
```

**Response:**
```json
{
  "count": 10,
  "sellers": [
    {
      "id": "seller-uuid",
      "email": "fisher@example.com",
      "user_type": "fisher",
      "name": "John Doe",
      "location": "Mwanza"
    }
  ]
}
```

---

### 6. **Audio Files**

#### Get Generated Audio
```http
GET /audio/{filename}
```

**Example:**
```http
GET /audio/price_alert_abc123.mp3
```

**Response:** Audio file (MP3)

---

## 🎯 **Frontend Integration Tips**

### 1. **Error Handling**
All endpoints return consistent error responses:
```json
{
  "status": "error",
  "message": "Error description"
}
```

### 2. **Loading States**
- `/api/analyze-catch` can take 10-30 seconds (AI processing)
- Show loading indicators for better UX
- Consider implementing progress bars

### 3. **Audio Integration**
```javascript
// Play generated audio
const audioUrl = response.voice_message_url;
if (audioUrl) {
  const audio = new Audio(audioUrl);
  audio.play();
}
```

### 4. **User Types**
```javascript
const USER_TYPES = {
  FISHER: "fisher",
  SELLER: "seller", 
  BUYER: "buyer"
};
```

### 5. **Currency Display**
All prices are in TZS (Tanzanian Shillings). Format for display:
```javascript
const formatPrice = (price) => `${price.toLocaleString()} TZS`;
```

---

## 🧪 **Testing Endpoints**

### Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "SamakiCash API is running!",
  "status": "healthy",
  "version": "1.0.0",
  "database": "PostgreSQL"
}
```

### Debug Endpoints (Development Only)
```http
GET /api/debug/users
GET /api/debug/catches
GET /api/debug/elevenlabs
```

---

## 🔧 **CORS Configuration**

The backend is configured to allow requests from:
- `https://samakicash-pwa.onrender.com` (production)
- `http://localhost:3000` (development)
- `http://localhost:8000` (local backend)

---

## 📱 **React/Next.js Integration Example**

```javascript
// API client setup
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Analyze catch function
const analyzeCatch = async (catchData) => {
  try {
    const response = await fetch(`${API_BASE}/api/analyze-catch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(catchData),
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      return result;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};

// Usage in component
const handleAnalyze = async () => {
  setLoading(true);
  try {
    const result = await analyzeCatch({
      fish_type: 'tilapia',
      quantity_kg: 15.5,
      location: 'Mwanza',
      user_id: currentUser.id,
      image_data: imageBase64 // if available
    });
    
    setAnalysisResult(result);
    
    // Play audio if available
    if (result.voice_message_url) {
      const audio = new Audio(`${API_BASE}${result.voice_message_url}`);
      audio.play();
    }
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

---

## 🚀 **Deployment Notes**

1. **Environment Variables**: Set `NEXT_PUBLIC_API_URL` to your production backend URL
2. **HTTPS**: Ensure your frontend uses HTTPS in production
3. **Error Boundaries**: Implement proper error handling for API failures
4. **Loading States**: Show appropriate loading indicators for long-running operations

---

## 📞 **Support**

If you encounter any issues:
1. Check the API health endpoint first
2. Verify CORS settings
3. Check browser network tab for detailed error messages
4. Contact the backend team with specific error details

---

**Happy coding! 🎉**
