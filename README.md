# 💼 Accounting API System

## 📋 Overview

Modern Flask-based accounting management system. Features JWT authentication, financial reporting, customer analysis, and cash flow tracking.

## 🚀 Features

### 💰 **Financial Management**
- ✅ Income/expense transaction tracking
- ✅ Financial summary reports
- ✅ Profit/loss calculations
- ✅ Cash flow analysis
- ✅ Monthly/yearly reporting

### 🧾 **Invoice Management**
- ✅ Invoice creation and tracking
- ✅ Invoice status analysis
- ✅ Customer-based invoice reports
- ✅ Payment status tracking

### 👥 **Customer Analysis**
- ✅ Customer-based financial analysis
- ✅ Invoice history tracking
- ✅ Customer profitability analysis
- ✅ Average invoice amounts

### 📊 **Reporting**
- ✅ Dashboard summary information
- ✅ Monthly detail reports
- ✅ Yearly financial summaries
- ✅ Transaction type analysis

## 🔧 Installation

### **Requirements**
```bash
pip install -r requirements.txt
```

### **Database Setup**
```python
from app import app, db
with app.app_context():
    db.create_all()
```

### **Running the Application**
```bash
python app.py
```

## 🛣️ API Endpoints

### **🔐 Authentication**
All accounting endpoints require JWT token.

```bash
# Login first to get token
POST /api/auth/login
```

### **💼 Financial Summary**
```bash
# General financial summary
GET /api/accounting/summary
GET /api/accounting/summary?start_date=2024-01-01&end_date=2024-12-31

# Response:
{
  "success": true,
  "summary": {
    "total_income": 50000.0,
    "total_expense": 30000.0,
    "net_profit": 20000.0,
    "income_transactions": 25,
    "expense_transactions": 15
  }
}
```

### **📅 Monthly Report**
```bash
# Specific month report
GET /api/accounting/monthly-report/2024/12

# Response:
{
  "success": true,
  "report": {
    "period": {
      "year": 2024,
      "month": 12,
      "month_name": "December"
    },
    "summary": {
      "total_income": 15000.0,
      "total_expense": 8000.0,
      "net_profit": 7000.0
    },
    "daily_breakdown": {...},
    "transactions": [...]
  }
}
```

### **💰 Cash Flow**
```bash
# Last 30 days cash flow
GET /api/accounting/cash-flow
GET /api/accounting/cash-flow?period_days=60

# Response:
{
  "success": true,
  "cash_flow": {
    "period": {
      "start_date": "2024-11-01",
      "end_date": "2024-11-30",
      "days": 30
    },
    "final_balance": 25000.0,
    "daily_flow": [
      {
        "date": "2024-11-01",
        "income": 2000.0,
        "expense": 500.0,
        "net_flow": 1500.0,
        "running_balance": 1500.0
      }
    ]
  }
}
```

### **👥 Customer Analysis**
```bash
# All customers analysis
GET /api/accounting/customer-analysis

# Specific customer analysis
GET /api/accounting/customer-analysis/1
GET /api/accounting/customer-analysis?customer_id=1

# Response:
{
  "success": true,
  "analysis": {
    "customer": {
      "id": 1,
      "name": "ABC Company",
      "email": "info@abc.com"
    },
    "invoice_summary": {
      "total_invoices": 10,
      "total_amount": 25000.0,
      "pending_invoices": 2,
      "paid_invoices": 8,
      "average_invoice_amount": 2500.0
    }
  }
}
```

### **🧾 Invoice Summary**
```bash
# Invoice status summary
GET /api/accounting/invoice-summary

# Response:
{
  "success": true,
  "invoice_summary": {
    "by_status": {
      "paid": {
        "count": 45,
        "total_amount": 75000.0
      },
      "pending": {
        "count": 8,
        "total_amount": 12000.0
      }
    }
  }
}
```

### **📈 Profit/Loss Report**
```bash
# Profit/loss calculation
GET /api/accounting/profit-loss
GET /api/accounting/profit-loss?start_date=2024-01-01&end_date=2024-12-31

# Response:
{
  "success": true,
  "profit_loss": {
    "revenue": {
      "total_revenue": 100000.0,
      "invoice_count": 50
    },
    "expenses": {
      "total_expenses": 60000.0,
      "expense_count": 35
    },
    "profit": {
      "gross_profit": 40000.0,
      "net_profit": 40000.0,
      "profit_margin": 40.0
    }
  }
}
```

### **📊 Dashboard**
```bash
# General dashboard information
GET /api/accounting/dashboard

# Response: Summary of all important metrics
{
  "success": true,
  "dashboard": {
    "financial_summary": {...},
    "invoice_summary": {...},
    "transaction_summary": {...},
    "cash_flow_summary": {...}
  }
}
```

### **📅 Yearly Report**
```bash
# Yearly detail report
GET /api/accounting/reports/yearly/2024

# Response: Yearly summary with monthly breakdown
```

### **🔍 Transaction Type Analysis**
```bash
# Summary by transaction types
GET /api/accounting/transaction-summary

# Response:
{
  "success": true,
  "transaction_summary": {
    "income": {
      "count": 50,
      "total_amount": 125000.0,
      "average_amount": 2500.0
    },
    "expense": {
      "count": 30,
      "total_amount": 75000.0,
      "average_amount": 2500.0
    }
  }
}
```

## 🔒 Security

### **JWT Authentication**
- All accounting endpoints require token
- Token duration: 24 hours
- Refresh token support

### **Role-Based Access**
- Admin: Access to all operations
- User: Limited access (own data)

## 📋 Usage Examples

### **Using API with Python**
```python
import requests

# Login and get token
login_response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = login_response.json()['token']

# Use token in headers
headers = {'Authorization': f'Bearer {token}'}

# Get financial summary
summary = requests.get(
    'http://localhost:5000/api/accounting/summary',
    headers=headers
)
print(summary.json())
```

### **cURL Examples**
```bash
# Get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Financial summary (with token)
curl -X GET http://localhost:5000/api/accounting/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Monthly report
curl -X GET http://localhost:5000/api/accounting/monthly-report/2024/12 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

### **Run All Tests**
```bash
python -m pytest tests/ -v
```

### **Specific Test Categories**
```bash
# Accounting services tests
python -m pytest tests/test_accounting_service.py -v

# Accounting routes tests
python -m pytest tests/test_accounting_routes.py -v

# Test runner script
python run_tests.py
```

## 📈 Performance

- **Fast Queries**: Optimized database queries with SQLAlchemy
- **Efficient Reporting**: Optimized for large datasets
- **Caching**: Cache support for repeated queries
- **Pagination**: Pagination for large result sets

## 🛠️ Technical Details

### **Technology Stack**
- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT
- **Testing**: pytest, pytest-flask

### **Project Structure**
```
Accounting/
├── app.py                 # Main application
├── models/               # Database models
├── services/             # Business logic
├── routes/               # API endpoints
├── utils/                # Helper functions
└── tests/                # Test files
```

## 🚀 Production Deployment

### **Environment Variables**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://...
```

### **Database Migration**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📞 Support

If you encounter any issues:
1. Run test commands
2. Check log files
3. Review API documentation

---

**Accounting API System** - Modern, secure, and user-friendly financial management solution 💼 