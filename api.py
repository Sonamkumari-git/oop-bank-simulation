from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Enterprise OOP Banking API")

# --- PYDANTIC SCHEMAS ---
class SignUpRequest(BaseModel):
    customer_id: str
    name: str

class LoginRequest(BaseModel):
    customer_id: str

class TransactionRequest(BaseModel):
    amount: float

class CreateAccountRequest(BaseModel):
    account_type: str  # "SAVINGS" or "CURRENT"
    initial_balance: float

def get_db_connection():
    conn = sqlite3.connect("bank_system.db")
    conn.row_factory = sqlite3.Row  
    return conn

@app.get("/")
def home():
    return {"status": "Active", "message": "Banking Core Engine Operating System Live."}

# 1. 🚀 NEW FEATURE: USER SIGN UP
@app.post("/auth/signup")
def signup(request: SignUpRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (request.customer_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Customer ID already registered. Choose another or login.")
    
    # Create the customer row
    cursor.execute("INSERT INTO customers (customer_id, name) VALUES (?, ?)", (request.customer_id, request.name))
    conn.commit()
    conn.close()
    return {"message": "Registration successful!", "customer_id": request.customer_id}

# 2. 🔑 NEW FEATURE: USER LOGIN
@app.post("/auth/login")
def login(request: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (request.customer_id,))
    customer = cursor.fetchone()
    conn.close()
    
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid Customer ID. Please sign up first.")
    return {"customer_id": customer["customer_id"], "name": customer["name"]}

# 3. ➕ NEW FEATURE: OPEN AN ACCOUNT VIA DASHBOARD
@app.post("/customers/{customer_id}/accounts/open")
def open_account(customer_id: str, request: CreateAccountRequest):
    if request.initial_balance < 0:
        raise HTTPException(status_code=400, detail="Opening balance cannot be negative.")
        
    import random
    prefix = "SAV" if request.account_type.upper() == "SAVINGS" else "CUR"
    generated_acc_num = f"{prefix}-{random.randint(10000, 99999)}"
    
    interest_rate = 0.04 if request.account_type.upper() == "SAVINGS" else 0.0
    overdraft_limit = 5000.0 if request.account_type.upper() == "CURRENT" else 0.0

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO accounts (account_number, customer_id, account_type, balance, interest_rate, overdraft_limit) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (generated_acc_num, customer_id, request.account_type.upper(), request.initial_balance, interest_rate, overdraft_limit))
    
    # Record initial transaction
    cursor.execute("INSERT INTO transactions (account_number, tx_type, amount) VALUES (?, 'INITIAL_DEPOSIT', ?)",
                   (generated_acc_num, request.initial_balance))
    
    conn.commit()
    conn.close()
    return {"message": f"{request.account_type} Account opened successfully!", "account_number": generated_acc_num}

# 4. FETCH ACCOUNTS & TRANSACTIONS
@app.get("/customers/{customer_id}/accounts")
def get_customer_accounts(customer_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE customer_id = ?", (customer_id,))
    accounts = cursor.fetchall()
    conn.close()
    return [dict(acc) for acc in accounts]

@app.get("/accounts/{account_number}/statement")
def get_statement(account_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tx_type, amount, timestamp FROM transactions WHERE account_number = ? ORDER BY id DESC", (account_number,))
    transactions = cursor.fetchall()
    conn.close()
    return [dict(tx) for tx in transactions]

# 5. CORE TRANSACTIONS
@app.post("/accounts/{account_number}/deposit")
def deposit_money(account_number: str, request: TransactionRequest):
    if request.amount <= 0: raise HTTPException(status_code=400, detail="Amount must be positive.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
    account = cursor.fetchone()
    if not account: raise HTTPException(status_code=404, detail="Account not found.")
    
    new_balance = account["balance"] + request.amount
    cursor.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (new_balance, account_number))
    cursor.execute("INSERT INTO transactions (account_number, tx_type, amount) VALUES (?, 'API_DEPOSIT', ?)", (account_number, request.amount))
    conn.commit(); conn.close()
    return {"new_balance": new_balance}

@app.post("/accounts/{account_number}/withdraw")
def withdraw_money(account_number: str, request: TransactionRequest):
    if request.amount <= 0: raise HTTPException(status_code=400, detail="Amount must be positive.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, overdraft_limit FROM accounts WHERE account_number = ?", (account_number,))
    account = cursor.fetchone()
    if not account: raise HTTPException(status_code=404, detail="Account not found.")
    
    if request.amount > (account["balance"] + account["overdraft_limit"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds! Limit exceeded.")
        
    new_balance = account["balance"] - request.amount
    cursor.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (new_balance, account_number))
    cursor.execute("INSERT INTO transactions (account_number, tx_type, amount) VALUES (?, 'API_WITHDRAW', ?)", (account_number, request.amount))
    conn.commit(); conn.close()
    return {"new_balance": new_balance}

class TransferRequest(BaseModel):
    target_account: str
    amount: float

# 6. 🚀 NEW FEATURE: ACCOUNT-TO-ACCOUNT TRANSFER
@app.post("/accounts/{source_account}/transfer")
def transfer_money(source_account: str, request: TransferRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Source Account check aur balance verify karo
    cursor.execute("SELECT balance FROM accounts WHERE account_number = ?", (source_account,))
    source = cursor.fetchone()
    if not source:
        conn.close()
        raise HTTPException(status_code=404, detail="Your account was not found.")
        
    if source["balance"] < request.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds for transfer!")
        
    # 2. Target Account check karo ki wo exist karta hai ya nahi
    cursor.execute("SELECT balance FROM accounts WHERE account_number = ?", (request.target_account,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=404, detail="Beneficiary account number does not exist.")
        
    # 3. Dono accounts ka balance update karo (Money debit & credit)
    new_source_balance = source["balance"] - request.amount
    new_target_balance = target["balance"] + request.amount
    
    cursor.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (new_source_balance, source_account))
    cursor.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (new_target_balance, request.target_account))
    
    # 4. Dono ke liye transaction history write karo
    import random
    tx_id = f"TXN{random.randint(100000, 999999)}"
    
    cursor.execute("INSERT INTO transactions (account_number, tx_type, amount) VALUES (?, ?, ?)", 
                   (source_account, f"TRANSFER TO {request.target_account} ({tx_id})", request.amount))
    cursor.execute("INSERT INTO transactions (account_number, tx_type, amount) VALUES (?, ?, ?)", 
                   (request.target_account, f"RECEIVED FROM {source_account} ({tx_id})", request.amount))
    
    conn.commit()
    conn.close()
    return {"message": "Transfer successful", "new_balance": new_source_balance, "tx_id": tx_id}