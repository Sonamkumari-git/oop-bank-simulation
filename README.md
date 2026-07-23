# Apex OOP Bank Simulation (Python)

A concise, object-oriented banking system simulation written in Python that demonstrates core banking concepts (Customers, Accounts, Transactions, interest, overdraft, transfers) and integrates with a Supabase (Postgres) cloud backend and a simple Streamlit UI.

---

## What this is
A small educational demo that models bank customers and account behaviors using OOP principles and provides two interfaces: a FastAPI-based HTTP API for core operations and a Streamlit front-end for interactive use. It is intended for learners who want to study OOP design, transaction flows, and a minimal cloud-backed persistence example.

### Stack
- **Language(s):** Python 3.9+
- **Framework / runtime:** FastAPI (API), Streamlit (UI), Uvicorn (ASGI server)
- **Notable libraries:** supabase-py, python-dotenv, pydantic, pandas, requests

---

## How it's organized
```
README.md                 # This file
requirements.txt          # Python dependencies
api.py                    # FastAPI application exposing banking endpoints (auth, accounts, txns)
app_ui.py                 # Streamlit user interface that calls the API
banking_models.py         # Core OOP models: Account, SavingsAccount, CurrentAccount, Customer, Transaction
database.py               # Supabase-backed persistence helpers (BankDatabase)
main.py                   # Demo script that runs a simulation and syncs data to Supabase
bank_system.db            # (unused) local SQLite DB snapshot included in the repo
__pycache__/              # Python bytecode cache (ignored in normal workflow)
.gitignore
```

How it fits together: main.py runs an in-memory simulation using classes in banking_models.py, then persists customers, accounts and transactions to the cloud via BankDatabase (database.py). The FastAPI app (api.py) implements HTTP endpoints that operate on Supabase tables and is the backend used by the Streamlit UI (app_ui.py) which provides a simple banking dashboard. The API and UI are decoupled: the UI makes HTTP requests to the API's endpoints.

## Environment and required secrets
This project expects the following environment variables (store them in a .env file or set in your environment):

- SUPABASE_URL — your Supabase project URL
- SUPABASE_KEY — a Supabase service role key or anon key with appropriate permissions

Do NOT commit secrets to the repository. The code loads environment variables via python-dotenv.

## How to run (shortest path)
1. Create and activate a Python 3.9+ virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. Provide environment variables (create a .env file):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_or_service_key
```

3. Run the FastAPI backend (local development):

```bash
uvicorn api:app --reload --port 8000
```

4. Run the Streamlit UI (in a separate terminal):

```bash
streamlit run app_ui.py
```

5. Optional: run the demo script that exercises the OOP models and syncs to Supabase:

```bash
python main.py
```

## Database / schema expectations
The API and BankDatabase assume the existence of three Supabase/Postgres tables with these columns (example):

- customers(customer_id text primary key, name text)
- accounts(account_number text primary key, customer_id text, account_type text, balance numeric, interest_rate numeric, overdraft_limit numeric)
- transactions(id serial primary key, account_number text, tx_type text, amount numeric, created_at timestamptz default now())

Create these tables in your Supabase project or adjust the code to match your schema.

## Notes, observations and recommended fixes
- README and code previously contained non-English comments; all code functions normally but comments should be English for broader audience (this file replaces the previous README).
- api.py raises a ValueError at import time if SUPABASE_URL or SUPABASE_KEY are missing; consider making the app start gracefully and return a 503 or a health endpoint if configuration is incomplete.
- Supabase operations in api.py are executed without explicit error handling — network or DB errors will raise exceptions. Wrap external calls with try/except and return meaningful HTTP errors.
- Transaction updates are not atomic. Transfers update source and target balances with separate update calls; consider using database-side transactions (Postgres transaction or RPC) or server-side stored procedure to avoid race conditions.
- The repo includes bank_system.db (SQLite) which appears unused. If not needed, remove it from the repository to reduce noise and possible sensitive data exposure.
- In banking_models.py, printing is used for errors and confirmation. For library usage prefer raising exceptions or returning structured results; keep print statements for CLI/demo only.

## Suggested next improvements (small prioritized list)
1. Add unit tests for banking_models (withdrawal, overdraft, transfers, interest calculation).
2. Make API operations transactional (atomic transfers) and add retries/optimistic locking for concurrent updates.
3. Add input validation and stricter Pydantic models for API requests (enforce min values, account format).
4. Provide Dockerfile and a docker-compose.yml for local development with a Postgres container instead of relying only on Supabase.

## Try asking
- How do I make transfers atomic across two account balance updates in api.py?
- The README mentions tables; can you provide SQL CREATE TABLE statements for customers/accounts/transactions?
- Where should I add unit tests for banking_models.py and what test cases should I cover?

---

If you want, I will commit this updated README.md to the repository now and also open a small PR-style commit message explaining the changes.