import os
from dotenv import load_dotenv
from supabase import create_client, Client
from banking_models import SavingsAccount, CurrentAccount, Customer, Transaction

# Ye line aapki .env file ko dhundhegi aur wahan se keys ko load karegi
load_dotenv()

class BankDatabase:
    """Ye class ab direct Supabase Cloud (PostgreSQL) se baat karegi"""
    
    def __init__(self):
        # .env file se URL aur Key fetch kar rahe hain
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        # Security check: Agar .env file me keys nahi mili toh error aayega
        if not self.url or not self.key:
            raise ValueError("🚨 Error: SUPABASE_URL ya SUPABASE_KEY .env file me nahi mili!")
            
        # Supabase se cloud connection ban raha hai
        self.supabase: Client = create_client(self.url, self.key)
        print("✅ Connected to Supabase Cloud Database Successfully!")

    def save_customer(self, customer: Customer):
        """Customer object ko Cloud table me save karega."""
        data = {
            "customer_id": customer.customer_id, 
            "name": customer.name
        }
        
        # 'upsert' ka matlab: Agar is ID ka customer pehle se hai toh details update kar do, nahi toh naya bana do
        self.supabase.table("customers").upsert(data).execute()
        print(f"☁️ Customer {customer.name} saved to Supabase Cloud.")

    def save_account(self, account, customer_id: str):
        """Account object aur uski transactions ko Cloud DB me save karega."""
        
        if isinstance(account, SavingsAccount):
            acc_type = "SAVINGS"
            interest_rate = account.interest_rate
            overdraft_limit = 0.0
        else:
            acc_type = "CURRENT"
            interest_rate = 0.0
            overdraft_limit = account.overdraft_limit

        # 1. Account ko save karne ka data
        account_data = {
            "account_number": account.account_number,
            "customer_id": customer_id,
            "account_type": acc_type,
            "balance": account.balance,
            "interest_rate": interest_rate,
            "overdraft_limit": overdraft_limit
        }
        
        # Account ko cloud me insert/update karna
        self.supabase.table("accounts").upsert(account_data).execute()

        # 2. Transactions save karna
        if account.transaction_history:
            transactions_data = []
            for tx in account.transaction_history:
                transactions_data.append({
                    "account_number": account.account_number,
                    "tx_type": tx.tx_type,
                    "amount": tx.amount
                    # timestamp cloud server khud daal dega
                })
            
            # Ek sath saari transactions insert kar do
            self.supabase.table("transactions").insert(transactions_data).execute()

        print(f"☁️ Account {account.account_number} synced with Supabase Cloud.")

    # SQLite me connection close karna padta tha, cloud API me iski zaroorat nahi hai isliye close() function hata diya hai.