from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Enterprise OOP Banking API")

# --- SUPABASE CONNECTION ---
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    raise ValueError("🚨 SUPABASE_URL ya SUPABASE_KEY missing hai .env me!")
supabase: Client = create_client(url, key)

# --- PYDANTIC SCHEMAS ---
class SignUpRequest(BaseModel):
    customer_id: str
    name: str

class LoginRequest(BaseModel):
    customer_id: str

class TransactionRequest(BaseModel):
    amount: float

class CreateAccountRequest(BaseModel):
    account_type: str
    initial_balance: float

class TransferRequest(BaseModel):
    target_account: str
    amount: float

@app.get("/")
def home():
    return {"status": "Active", "message": "Banking Core Engine Running on Supabase."}

@app.post("/auth/signup")
def signup(request: SignUpRequest):
    # Check if user exists
    existing = supabase.table("customers").select("*").eq("customer_id", request.customer_id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Customer ID already registered.")
    
    # Insert new user
    supabase.table("customers").insert({"customer_id": request.customer_id, "name": request.name}).execute()
    return {"message": "Registration successful!", "customer_id": request.customer_id}

@app.post("/auth/login")
def login(request: LoginRequest):
    res = supabase.table("customers").select("*").eq("customer_id", request.customer_id).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid Customer ID.")
    return res.data[0]

@app.post("/customers/{customer_id}/accounts/open")
def open_account(customer_id: str, request: CreateAccountRequest):
    if request.initial_balance < 0:
        raise HTTPException(status_code=400, detail="Opening balance cannot be negative.")
        
    prefix = "SAV" if request.account_type.upper() == "SAVINGS" else "CUR"
    generated_acc_num = f"{prefix}-{random.randint(10000, 99999)}"
    interest_rate = 0.04 if request.account_type.upper() == "SAVINGS" else 0.0
    overdraft_limit = 5000.0 if request.account_type.upper() == "CURRENT" else 0.0

    account_data = {
        "account_number": generated_acc_num,
        "customer_id": customer_id,
        "account_type": request.account_type.upper(),
        "balance": request.initial_balance,
        "interest_rate": interest_rate,
        "overdraft_limit": overdraft_limit
    }
    supabase.table("accounts").insert(account_data).execute()
    
    tx_data = {
        "account_number": generated_acc_num,
        "tx_type": "INITIAL_DEPOSIT",
        "amount": request.initial_balance
    }
    supabase.table("transactions").insert(tx_data).execute()
    
    return {"message": f"{request.account_type} Account opened successfully!", "account_number": generated_acc_num}

@app.get("/customers/{customer_id}/accounts")
def get_customer_accounts(customer_id: str):
    res = supabase.table("accounts").select("*").eq("customer_id", customer_id).execute()
    return res.data

@app.get("/accounts/{account_number}/statement")
def get_statement(account_number: str):
    res = supabase.table("transactions").select("tx_type, amount, created_at").eq("account_number", account_number).order("created_at", desc=True).execute()
    return res.data

@app.post("/accounts/{account_number}/deposit")
def deposit_money(account_number: str, request: TransactionRequest):
    if request.amount <= 0: 
        raise HTTPException(status_code=400, detail="Amount must be positive.")
    
    acc_res = supabase.table("accounts").select("balance").eq("account_number", account_number).execute()
    if not acc_res.data: raise HTTPException(status_code=404, detail="Account not found.")
    
    new_balance = acc_res.data[0]["balance"] + request.amount
    supabase.table("accounts").update({"balance": new_balance}).eq("account_number", account_number).execute()
    supabase.table("transactions").insert({"account_number": account_number, "tx_type": "API_DEPOSIT", "amount": request.amount}).execute()
    
    return {"new_balance": new_balance}

@app.post("/accounts/{account_number}/withdraw")
def withdraw_money(account_number: str, request: TransactionRequest):
    if request.amount <= 0: 
        raise HTTPException(status_code=400, detail="Amount must be positive.")
        
    acc_res = supabase.table("accounts").select("balance, overdraft_limit").eq("account_number", account_number).execute()
    if not acc_res.data: raise HTTPException(status_code=404, detail="Account not found.")
    
    acc = acc_res.data[0]
    if request.amount > (acc["balance"] + acc["overdraft_limit"]):
        raise HTTPException(status_code=400, detail="Insufficient funds! Limit exceeded.")
        
    new_balance = acc["balance"] - request.amount
    supabase.table("accounts").update({"balance": new_balance}).eq("account_number", account_number).execute()
    supabase.table("transactions").insert({"account_number": account_number, "tx_type": "API_WITHDRAW", "amount": request.amount}).execute()
    
    return {"new_balance": new_balance}

@app.post("/accounts/{source_account}/transfer")
def transfer_money(source_account: str, request: TransferRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive.")
        
    source_res = supabase.table("accounts").select("balance").eq("account_number", source_account).execute()
    if not source_res.data: raise HTTPException(status_code=404, detail="Source account not found.")
    
    if source_res.data[0]["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for transfer!")
        
    target_res = supabase.table("accounts").select("balance").eq("account_number", request.target_account).execute()
    if not target_res.data: raise HTTPException(status_code=404, detail="Beneficiary account not found.")
    
    new_source_balance = source_res.data[0]["balance"] - request.amount
    new_target_balance = target_res.data[0]["balance"] + request.amount
    
    supabase.table("accounts").update({"balance": new_source_balance}).eq("account_number", source_account).execute()
    supabase.table("accounts").update({"balance": new_target_balance}).eq("account_number", request.target_account).execute()
    
    tx_id = f"TXN{random.randint(100000, 999999)}"
    supabase.table("transactions").insert([
        {"account_number": source_account, "tx_type": f"TRANSFER TO {request.target_account} ({tx_id})", "amount": request.amount},
        {"account_number": request.target_account, "tx_type": f"RECEIVED FROM {source_account} ({tx_id})", "amount": request.amount}
    ]).execute()
    
    return {"message": "Transfer successful", "new_balance": new_source_balance, "tx_id": tx_id}
