# Apex OOP Bank Simulation

A professional-grade, Object-Oriented Banking System simulation built with Python that demonstrates core banking operations and integrates with a live Supabase cloud database. The system exposes a RESTful API and provides an interactive web-based user interface.

**🚀 Live Demo:** [https://oop-bank-simulation-frontend.onrender.com](https://oop-bank-simulation-frontend.onrender.com)

---

## 📋 Project Overview

This project implements a complete banking simulation system using Object-Oriented Programming (OOP) principles. It models real-world banking entities (Customers, Accounts, Transactions) and supports core banking operations such as deposits, withdrawals, transfers, interest calculation, and overdraft management.

The system is designed with a **three-tier architecture**:
- **Backend API**: FastAPI-based REST service for core banking operations
- **Frontend UI**: Streamlit-based interactive dashboard
- **Database Layer**: Supabase (PostgreSQL) for persistent cloud storage

---

## 🔧 Technology Stack

### **Core Technologies**

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Primary development language |
| **Backend API** | FastAPI | Latest | Modern async web framework for REST endpoints |
| **Web Server** | Uvicorn | Latest | ASGI application server for production deployment |
| **Frontend UI** | Streamlit | Latest | Interactive web interface for user interactions |
| **Database** | Supabase (PostgreSQL) | Cloud | Managed cloud database with real-time capabilities |
| **ORM/Query** | Supabase Python SDK | Latest | Cloud database client library |

### **Dependencies & Libraries**

```
Core Framework & API:
  - fastapi         → Modern web framework with automatic API documentation
  - uvicorn         → ASGI server for deploying FastAPI applications
  - streamlit       → Rapid prototyping framework for data applications
  
Database & Cloud:
  - supabase        → Python client for Supabase cloud database
  
Data Validation & Serialization:
  - pydantic        → Data validation using Python type annotations
  - pandas          → Data manipulation and analysis
  
Utilities:
  - python-dotenv   → Environment variable management (security)
  - requests        → HTTP client library for API calls
```

### **Architecture Highlights**

- **Object-Oriented Design**: Inheritance, polymorphism, and encapsulation demonstrated through Account hierarchy
- **Abstract Base Classes**: Account (ABC) with concrete implementations (SavingsAccount, CurrentAccount)
- **Composition Pattern**: Customer contains multiple Account instances
- **Exception Handling**: Custom InsufficientFundsException for business logic
- **Data Validation**: Pydantic models for type-safe request/response handling

---

## 📁 Project Structure

```
oop-bank-simulation/
│
├── README.md                 # Project documentation (this file)
├── requirements.txt          # Python package dependencies
│
├── banking_models.py         # Core OOP models
│   ├── Account (Abstract)
│   ├── SavingsAccount
│   ├── CurrentAccount
│   ├── Customer
│   └── Transaction
│
├── api.py                    # FastAPI REST endpoints
│   ├── /auth/signup          - Customer registration
│   ├── /auth/login           - Customer authentication
│   ├── /accounts/open        - Open new account
│   ├── /accounts/statement   - Transaction history
│   ├── /deposit              - Deposit funds
│   ├── /withdraw             - Withdraw funds
│   └── /transfer             - Transfer between accounts
│
├── app_ui.py                 # Streamlit user interface
│   └── Interactive dashboard for banking operations
│
├── database.py               # Supabase integration layer
│   └── BankDatabase class for cloud persistence
│
├── main.py                   # Demo & simulation script
│   └── End-to-end workflow demonstration
│
└── .gitignore               # Git ignore rules
```

---

## 🏗️ System Architecture

### **Data Flow**

```
User Interface (Streamlit)
        ↓
    HTTP Requests
        ↓
FastAPI Backend (api.py)
        ↓
Business Logic (banking_models.py)
        ↓
Database Layer (database.py)
        ↓
Supabase Cloud Database (PostgreSQL)
```

### **Core Models**

#### **Account Hierarchy** (Polymorphism Example)
```
Account (Abstract Base Class)
├── SavingsAccount
│   ├── No overdraft allowed
│   ├── Yields interest (4% annually)
│   └── Strict balance checks
│
└── CurrentAccount
    ├── Overdraft facility allowed (default ₹10,000)
    ├── No interest accrual
    └── Business-friendly rules
```

#### **Key Classes**

- **Transaction**: Records individual banking transactions with timestamps
- **Customer**: Manages customer identity and linked accounts
- **BankDatabase**: Handles Supabase synchronization and persistence

---

## 🚀 Quick Start Guide

### **Prerequisites**

- Python 3.9 or higher
- Supabase account (free tier available at [supabase.com](https://supabase.com))
- pip package manager

### **Step 1: Clone & Setup Environment**

```bash
# Clone the repository
git clone https://github.com/Sonamkumari-git/oop-bank-simulation.git
cd oop-bank-simulation

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configure Supabase Credentials**

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_or_service_role_key
```

**Note**: Never commit `.env` to version control. The `.gitignore` file should already exclude it.

To obtain these credentials:
1. Go to [app.supabase.com](https://app.supabase.com)
2. Create a new project or select an existing one
3. Navigate to **Settings → API**
4. Copy your project URL and service role key

### **Step 3: Setup Database Schema**

Run the following SQL in your Supabase SQL Editor to create required tables:

```sql
-- Create customers table
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create accounts table
CREATE TABLE accounts (
    account_number TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance NUMERIC DEFAULT 0,
    interest_rate NUMERIC DEFAULT 0,
    overdraft_limit NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_number TEXT NOT NULL,
    tx_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);

-- Create indexes for performance
CREATE INDEX idx_customer_id ON accounts(customer_id);
CREATE INDEX idx_account_number ON transactions(account_number);
```

### **Step 4: Run the Application**

**Terminal 1 - Start FastAPI Backend:**
```bash
uvicorn api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
API documentation: `http://localhost:8000/docs` (Swagger UI)

**Terminal 2 - Start Streamlit Frontend:**
```bash
streamlit run app_ui.py
```

The UI will be available at `http://localhost:8501`

### **Step 5 (Optional): Run Demo Script**

```bash
python main.py
```

This demonstrates the OOP models and syncs sample data to Supabase.

---

## 📊 API Endpoints Reference

### **Authentication**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register a new customer |
| POST | `/auth/login` | Authenticate customer |

### **Account Management**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers/{customer_id}/accounts/open` | Create new account |
| GET | `/customers/{customer_id}/accounts` | List all customer accounts |

### **Transactions**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts/{account_number}/statement` | Fetch transaction history |
| POST | `/accounts/{account_number}/deposit` | Deposit funds |
| POST | `/accounts/{account_number}/withdraw` | Withdraw funds |
| POST | `/accounts/{source_account}/transfer` | Transfer between accounts |

### **Request/Response Examples**

#### Create Account
```bash
curl -X POST http://localhost:8000/customers/CUST001/accounts/open \
  -H "Content-Type: application/json" \
  -d '{
    "account_type": "SAVINGS",
    "initial_balance": 5000.0
  }'
```

#### Deposit Funds
```bash
curl -X POST http://localhost:8000/accounts/SAV-12345/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000.0}'
```

#### Transfer Money
```bash
curl -X POST http://localhost:8000/accounts/SAV-12345/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "target_account": "CUR-54321",
    "amount": 500.0
  }'
```

---

## 🧪 OOP Features Demonstrated

### **1. Inheritance & Polymorphism**
- Abstract `Account` class with concrete `SavingsAccount` and `CurrentAccount` implementations
- Each account type overrides the `withdraw()` method with type-specific business rules

### **2. Encapsulation**
- Protected `_balance` attribute with read-only `@property` getter
- Transaction history maintained internally

### **3. Composition**
- `Customer` class aggregates multiple `Account` instances
- `Transaction` objects composed within accounts

### **4. Exception Handling**
- Custom `InsufficientFundsException` for business logic violations
- Graceful error handling throughout the API

### **5. Data Validation**
- Pydantic models enforce type safety and request validation
- Negative amount checks at business logic layer

---

## 🔐 Security Considerations

1. **Environment Variables**: Never hardcode Supabase credentials; use `.env` files
2. **Request Validation**: All inputs validated through Pydantic schemas
3. **Database Constraints**: Foreign keys and primary keys enforce referential integrity
4. **Error Handling**: Sensitive information not exposed in API error messages

### **Recommended Security Enhancements**

- Implement JWT-based authentication for API endpoints
- Add role-based access control (RBAC)
- Use Supabase Row Level Security (RLS) policies
- Implement rate limiting on API endpoints
- Add HTTPS/TLS in production

---

## 🚢 Deployment

### **Render.com Deployment** (Frontend - Streamlit)

```bash
# Push to GitHub
git push origin main

# In Render Dashboard:
# 1. Create new Web Service
# 2. Connect GitHub repository
# 3. Set build command: pip install -r requirements.txt
# 4. Set start command: streamlit run app_ui.py --server.port 10000
# 5. Add environment variables from .env
```

### **FastAPI Backend Deployment**

Deploy on platforms like:
- Render.com
- Railway.app
- Heroku
- DigitalOcean App Platform

Example for Render:
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn api:app --host 0.0.0.0 --port 10000
```

---

## 🐛 Known Issues & Limitations

1. **Non-Atomic Transfers**: Account transfers execute sequentially; consider database-level transactions
2. **No Transaction Rollback**: Failed operations don't auto-rollback; manual reconciliation needed
3. **Limited Error Handling**: API lacks comprehensive error recovery mechanisms
4. **Concurrent Updates**: No optimistic locking for simultaneous updates
5. **Input Validation**: Could be stricter (e.g., enforce minimum amounts, account format)
6. **Logging**: Minimal logging; should implement structured logging for debugging

---

## 📈 Future Enhancement Roadmap

### **Priority 1 - Core Functionality**
- [ ] Implement unit tests for `banking_models.py` (target: 85%+ coverage)
- [ ] Add atomic database transactions for transfers
- [ ] Implement JWT authentication and authorization
- [ ] Add comprehensive API error handling and logging

### **Priority 2 - Data Integrity**
- [ ] Add database-level constraints and triggers
- [ ] Implement optimistic locking for concurrent updates
- [ ] Add transaction rollback capability
- [ ] Implement audit logging

### **Priority 3 - DevOps & Monitoring**
- [ ] Create Dockerfile and docker-compose.yml
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Implement structured logging (e.g., ELK stack)
- [ ] Add monitoring and alerting (e.g., Sentry)

### **Priority 4 - Features**
- [ ] Multi-currency support
- [ ] Scheduled transaction processing
- [ ] Loan management module
- [ ] Advanced reporting and analytics

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Supabase Documentation](https://supabase.com/docs)
- [Python OOP Concepts](https://docs.python.org/3/tutorial/classes.html)
- [RESTful API Design](https://restfulapi.net/)

---

## 📝 Common Troubleshooting

### **Issue: "SUPABASE_URL or SUPABASE_KEY missing"**
- **Solution**: Ensure `.env` file is created with correct credentials
- Verify `.env` is in the project root directory
- Check credentials are exactly as provided by Supabase

### **Issue: "ModuleNotFoundError: No module named 'supabase'"**
- **Solution**: Ensure virtual environment is activated and dependencies installed
- Run: `pip install -r requirements.txt`

### **Issue: "Connection refused" on localhost:8000**
- **Solution**: Verify FastAPI server is running
- Check if port 8000 is already in use: `lsof -i :8000` (macOS/Linux)

### **Issue: Database operations fail silently**
- **Solution**: Check Supabase credentials and network connectivity
- Verify table schemas match expected structure
- Review API logs for detailed error information

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ✉️ Support & Contact

For questions, issues, or suggestions:
- Open an GitHub Issue: [Issues](https://github.com/Sonamkumari-git/oop-bank-simulation/issues)
- Check existing documentation in this README
- Review API documentation at `http://localhost:8000/docs`

---

## 🎯 Key Takeaways

This project demonstrates:
- ✅ **Professional Python OOP design** with inheritance and polymorphism
- ✅ **Production-ready REST API** with FastAPI
- ✅ **Cloud database integration** with Supabase
- ✅ **Interactive web interface** with Streamlit
- ✅ **Real-world banking concepts** (accounts, transactions, interest, overdraft)
- ✅ **Scalable architecture** for educational and enterprise use

---

**Last Updated**: July 2026  
**Version**: 1.0.0  
**Maintainer**: Sonam Kumar