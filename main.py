from banking_models import SavingsAccount, CurrentAccount, Customer, InsufficientFundsException
from database import BankDatabase  

def run_banking_simulation():
    print("=== STARTING PHASE 1: CORE OOP BANKING SYSTEM SIMULATION ===\n")

    # 1. Create Customers
    rahul = Customer(name="Rahul Sharma", customer_id="CUST101")
    amit = Customer(name="Amit Verma", customer_id="CUST102")

    # 2. Create and Link Accounts
    rahul_savings = SavingsAccount(account_number="SAV-R101", initial_balance=5000.0)
    rahul_current = CurrentAccount(account_number="CUR-R102", initial_balance=2000.0, overdraft_limit=5000.0)
    rahul.link_account(rahul_savings)
    rahul.link_account(rahul_current)

    amit_savings = SavingsAccount(account_number="SAV-A201", initial_balance=10000.0)
    amit.link_account(amit_savings)

    print("\n" + "="*50 + "\n⚙️ TESTING BUSINESS RULES\n" + "="*50)

    # 3. Normal Operations & Exception Handling
    rahul_savings.deposit(1500.0)
    rahul_current.withdraw(6000.0)
    
    try:
        rahul_savings.withdraw(8000.0)
    except InsufficientFundsException as e:
        print(f"Expected Exception Caught Successfully:\n👉 {e}")

    # 4. Transfers & Interest
    amit_savings.transfer(target_account=rahul_current, amount=3000.0)
    rahul_savings.calculate_and_apply_interest()

    print("\n" + "="*50 + "\n📜 PRINTING FINAL STATEMENTS\n" + "="*50)
    for line in rahul_savings.get_statement():
        print(line)
    for line in rahul_current.get_statement():
        print(line)
        
    print(f"👤 Customer: {rahul.name} | Net Worth in Bank: ₹{rahul.get_net_worth():,.2f}")
    print(f"👤 Customer: {amit.name} | Net Worth in Bank: ₹{amit.get_net_worth():,.2f}")

    # ==========================================
    # 🚀 NAYA CODE: PHASE 2 - DATABASE SAVING (SUPABASE CLOUD)
    # ==========================================
    print("\n" + "="*50 + "\n☁️ SAVING DATA TO SUPABASE CLOUD DATABASE\n" + "="*50)
    
    # 1. Cloud Database se connect karo (Ab yahan db name pass nahi karna hai)
    db = BankDatabase()
    
    # 2. Customers save karo
    db.save_customer(rahul)
    db.save_customer(amit)
    
    # 3. Accounts aur unki transactions save karo
    db.save_account(rahul_savings, rahul.customer_id)
    db.save_account(rahul_current, rahul.customer_id)
    db.save_account(amit_savings, amit.customer_id)
    
    # db.close() hata diya gaya hai kyunki Cloud API ko close nahi karna padta
    print("✅ All data safely stored in Supabase Cloud!")

if __name__ == "__main__":
    run_banking_simulation()