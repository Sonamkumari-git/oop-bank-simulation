from abc import ABC, abstractmethod
from datetime import datetime

class InsufficientFundsException(Exception):
    """Custom exception raised when an account has insufficient funds."""
    pass

class Transaction:
    """Class to keep a record of each transaction."""
    def __init__(self, tx_type: str, amount: float):
        self.timestamp = datetime.now()
        self.tx_type = tx_type
        self.amount = amount

    def __str__(self) -> str:
        time_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # We format the currency value first, then align the resulting string cleanly
        formatted_amount = f"₹{self.amount:,.2f}"
        return f"[{time_str}] {self.tx_type:<20} | {formatted_amount:>15}"

class Account(ABC):
    """Abstract Base Class - Cannot be instantiated directly."""
    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self._balance = initial_balance  # Encapsulated state (protected attribute)
        self.transaction_history: list[Transaction] = []
        
        if initial_balance > 0:
            self.transaction_history.append(Transaction("INITIAL_DEPOSIT", initial_balance))

    @property
    def balance(self) -> float:
        """Getter to make the balance read-only outside the class."""
        return self._balance

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("❌ Error: Deposit amount cannot be zero or negative.")
            return False
        self._balance += amount
        self.transaction_history.append(Transaction("DEPOSIT", amount))
        return True

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Each subclass will override this according to its specific rules."""
        pass

    def transfer(self, target_account: 'Account', amount: float) -> bool:
        """Polymorphism: This method accepts any target Account type."""
        if amount <= 0:
            print("❌ Error: Transfer amount cannot be zero or negative.")
            return False
            
        try:
            # First attempt to withdraw from the current account
            if self.withdraw(amount):
                target_account.deposit(amount)
                self.transaction_history.append(Transaction(f"TRANSFER_TO_{target_account.account_number}", amount))
                target_account.transaction_history.append(Transaction(f"TRANSFER_FROM_{self.account_number}", amount))
                return True
        except InsufficientFundsException as e:
            print(f"❌ Transfer Failed: {e}")
        return False

    def get_statement(self) -> list[str]:
        lines = [f"\n=========================================",
                 f"STATEMENT FOR ACCOUNT: {self.account_number}",
                 f"========================================="]
        for tx in self.transaction_history:
            lines.append(str(tx))
        lines.append(f"-----------------------------------------")
        lines.append(f"Final Balance: ₹{self._balance:,.2f}")
        lines.append(f"=========================================\n")
        return lines


class SavingsAccount(Account):
    """Savings Account: No overdraft allowed, yields interest."""
    def __init__(self, account_number: str, initial_balance: float = 0.0, interest_rate: float = 0.04):
        super().__init__(account_number, initial_balance)
        self.interest_rate = interest_rate

    def withdraw(self, amount: float) -> bool:
        # Method Overriding: Strict balance check
        if amount <= 0:
            print("❌ Error: Withdrawal amount must be greater than zero.")
            return False
        if amount > self._balance:
            raise InsufficientFundsException(f"Insufficient balance in Savings Account {self.account_number}. Available: ₹{self._balance:,.2f}")
        
        self._balance -= amount
        self.transaction_history.append(Transaction("WITHDRAWAL", amount))
        return True

    def calculate_and_apply_interest(self):
        """Savings-specific method to calculate and apply interest."""
        interest = self._balance * self.interest_rate
        if interest > 0:
            self._balance += interest
            self.transaction_history.append(Transaction("INTEREST_CREDIT", interest))
            print(f"💰 ₹{interest:,.2f} interest credited to Account {self.account_number}.")


class CurrentAccount(Account):
    """Current Account: Overdraft facility is allowed up to a specific limit."""
    def __init__(self, account_number: str, initial_balance: float = 0.0, overdraft_limit: float = 10000.0):
        super().__init__(account_number, initial_balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> bool:
        # Method Overriding: Balance + Overdraft limit check
        if amount <= 0:
            print("❌ Error: Withdrawal amount must be greater than zero.")
            return False
        
        max_allowed = self._balance + self.overdraft_limit
        if amount > max_allowed:
            raise InsufficientFundsException(f"Overdraft limit exceeded for Current Account {self.account_number}. Max available: ₹{max_allowed:,.2f}")
        
        self._balance -= amount
        self.transaction_history.append(Transaction("WITHDRAWAL", amount))
        return True


class Customer:
    """Composition Example: A customer can have multiple accounts."""
    def __init__(self, name: str, customer_id: str):
        self.name = name
        self.customer_id = customer_id
        self.accounts: dict[str, Account] = {}

    def link_account(self, account: Account):
        self.accounts[account.account_number] = account
        print(f"✅ Account {account.account_number} linked to Customer {self.name}.")

    def get_net_worth(self) -> float:
        return sum(acc.balance for acc in self.accounts.values())