# 💼 Accounting API System

## 📋 Overview

Modern Flask-based accounting management system with comprehensive transaction management. Features JWT authentication, financial reporting, customer analysis, cash flow tracking, and complete transaction CRUD operations with advanced filtering and statistics.

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

### 💳 **Transaction Management**
- ✅ Complete CRUD operations for transactions
- ✅ Transaction creation and updates
- ✅ Transaction search and filtering
- ✅ Transaction statistics and analytics
- ✅ Type-based transaction categorization
- ✅ Invoice-based transaction tracking
- ✅ Paginated transaction listings

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

### **💳 Transaction Management**
```bash
# Get all transactions (paginated)
GET /api/transactions/
GET /api/transactions/?page=1&per_page=10

# Response:
{
  "success": true,
  "transactions": [
    {
      "id": 1,
      "invoice_id": 5,
      "amount": 1500.0,
      "date": "2024-01-15",
      "type": "payment",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 25,
  "pages": 3,
  "current_page": 1,
  "per_page": 10
}

# Get specific transaction
GET /api/transactions/1

# Create new transaction
POST /api/transactions/
{
  "invoice_id": 5,
  "amount": 1500.0,
  "date": "2024-01-15",
  "type": "payment"
}

# Update transaction
PUT /api/transactions/1
{
  "amount": 1750.0,
  "type": "refund"
}

# Delete transaction
DELETE /api/transactions/1

# Get transactions by invoice
GET /api/transactions/by-invoice/5

# Get transactions by type
GET /api/transactions/by-type/payment

# Search transactions
GET /api/transactions/search?q=payment

# Get transaction statistics
GET /api/transactions/stats

# Response:
{
  "success": true,
  "statistics": {
    "total_transactions": 150,
    "total_amount": 75000.0,
    "by_type": {
      "payment": {
        "count": 120,
        "total_amount": 65000.0
      },
      "refund": {
        "count": 30,
        "total_amount": 10000.0
      }
    },
    "monthly": {
      "2024-01": {
        "count": 25,
        "total_amount": 12500.0
      }
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

# Create a new transaction
transaction_data = {
    'invoice_id': 5,
    'amount': 1500.0,
    'date': '2024-01-15',
    'type': 'payment'
}
create_response = requests.post(
    'http://localhost:5000/api/transactions/',
    json=transaction_data,
    headers=headers
)
print(create_response.json())

# Get transaction statistics
stats_response = requests.get(
    'http://localhost:5000/api/transactions/stats',
    headers=headers
)
print(stats_response.json())

# Search transactions
search_response = requests.get(
    'http://localhost:5000/api/transactions/search?q=payment',
    headers=headers
)
print(search_response.json())
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

# Create transaction
curl -X POST http://localhost:5000/api/transactions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"invoice_id":5,"amount":1500.0,"date":"2024-01-15","type":"payment"}'

# Get all transactions
curl -X GET http://localhost:5000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get transactions by invoice
curl -X GET http://localhost:5000/api/transactions/by-invoice/5 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search transactions
curl -X GET http://localhost:5000/api/transactions/search?q=payment \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get transaction statistics
curl -X GET http://localhost:5000/api/transactions/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update transaction
curl -X PUT http://localhost:5000/api/transactions/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":1750.0,"type":"refund"}'

# Delete transaction
curl -X DELETE http://localhost:5000/api/transactions/1 \
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

# Transaction services tests
python -m pytest tests/test_services.py::TestTransactionService -v

# Transaction routes tests
python -m pytest tests/test_transaction_routes.py -v

# All transaction tests
python -m pytest tests/test_transaction_routes.py tests/test_services.py::TestTransactionService -v

# User and authentication tests
python -m pytest tests/test_user_routes.py tests/test_auth_routes.py -v

# Invoice tests
python -m pytest tests/test_invoice_routes.py -v

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