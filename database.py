"""
Digital Banking System - Database Engine
Relational Schema & PL/SQL Logic Implementation
Strict adherence to BACSE202 DA-2 Schema & Normalization (BCNF)
"""

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # SECTION 1: DDL - TABLE CREATION
    cursor.executescript("""
    DROP TABLE IF EXISTS Beneficiary;
    DROP TABLE IF EXISTS Loan;
    DROP TABLE IF EXISTS TransactionLog;
    DROP TABLE IF EXISTS Account;
    DROP TABLE IF EXISTS LoanScheme;
    DROP TABLE IF EXISTS Admin;
    DROP TABLE IF EXISTS Customer;
    DROP TABLE IF EXISTS Branch;

    -- Branch Table
    CREATE TABLE Branch (
        BranchCode VARCHAR(10) PRIMARY KEY,
        BranchName VARCHAR(50) NOT NULL,
        BranchAddress VARCHAR(100)
    );

    -- Customer Table
    CREATE TABLE Customer (
        CustomerID INTEGER PRIMARY KEY,
        Name VARCHAR(50) NOT NULL,
        Email VARCHAR(50) UNIQUE NOT NULL,
        Phone VARCHAR(15),
        Address VARCHAR(100),
        DOB DATE,
        PasswordHash VARCHAR(100) NOT NULL,
        UpiId VARCHAR(50) UNIQUE,
        Avatar VARCHAR(255)
    );

    -- Admin Table
    CREATE TABLE Admin (
        AdminID INTEGER PRIMARY KEY,
        Name VARCHAR(50) NOT NULL,
        Email VARCHAR(50) UNIQUE NOT NULL,
        Role VARCHAR(30)
    );

    -- LoanScheme Table
    CREATE TABLE LoanScheme (
        LoanType VARCHAR(30) PRIMARY KEY,
        InterestRate REAL NOT NULL
    );

    -- Account Table
    CREATE TABLE Account (
        AccountNo INTEGER PRIMARY KEY,
        CustomerID INTEGER NOT NULL,
        BranchCode VARCHAR(10) NOT NULL,
        AccountType VARCHAR(20) CHECK (AccountType IN ('Savings', 'Current')),
        Balance REAL DEFAULT 0 CHECK (Balance >= 0),
        OpenDate DATE DEFAULT CURRENT_TIMESTAMP,
        Status VARCHAR(15) DEFAULT 'Active',
        UpiPin VARCHAR(6) DEFAULT '1234',
        CONSTRAINT fk_acc_cust FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
        CONSTRAINT fk_acc_branch FOREIGN KEY (BranchCode) REFERENCES Branch(BranchCode)
    );

    -- TransactionLog Table
    CREATE TABLE TransactionLog (
        TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
        AccountNo INTEGER NOT NULL,
        TxnType VARCHAR(15) CHECK (TxnType IN ('Deposit', 'Withdraw', 'Transfer')),
        Amount REAL NOT NULL CHECK (Amount > 0),
        TxnDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Description VARCHAR(100),
        TargetAccountNo INTEGER,
        ReferenceRef VARCHAR(50),
        CONSTRAINT fk_txn_acc FOREIGN KEY (AccountNo) REFERENCES Account(AccountNo)
    );

    -- Loan Table
    CREATE TABLE Loan (
        LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER NOT NULL,
        AdminID INTEGER,
        LoanType VARCHAR(30) NOT NULL,
        Amount REAL NOT NULL CHECK (Amount > 0),
        Status VARCHAR(15) DEFAULT 'Pending',
        ApplyDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        TenureMonths INTEGER DEFAULT 24,
        CONSTRAINT fk_loan_cust FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
        CONSTRAINT fk_loan_admin FOREIGN KEY (AdminID) REFERENCES Admin(AdminID),
        CONSTRAINT fk_loan_type FOREIGN KEY (LoanType) REFERENCES LoanScheme(LoanType)
    );

    -- Beneficiary Table
    CREATE TABLE Beneficiary (
        BeneficiaryID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER NOT NULL,
        BeneficiaryAccNo INTEGER NOT NULL,
        BeneficiaryName VARCHAR(50) NOT NULL,
        BankName VARCHAR(50),
        NickName VARCHAR(50),
        CONSTRAINT fk_ben_cust FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
    );
    """)

    # SECTION 2: SAMPLE DATA SEEDING (Matching Assignment DA-2)
    # Seed Branches
    cursor.execute("INSERT INTO Branch VALUES ('BR01', 'Bank of Baroda Chennai Main', '12 Anna Salai, Chennai, TN')")
    cursor.execute("INSERT INTO Branch VALUES ('BR02', 'Bank of Baroda Coimbatore East', '45 RS Puram, Coimbatore, TN')")

    # Seed Customers
    cursor.execute("INSERT INTO Customer VALUES (101, 'Sricharan K', 'sricharan@email.com', '9876543210', 'Tambaram, Chennai', '2004-05-12', 'hash_abc123', 'sricharan@bob', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sricharan')")
    cursor.execute("INSERT INTO Customer VALUES (102, 'Divya R', 'divya@email.com', '9876500011', 'Coimbatore', '2003-11-02', 'hash_def456', 'divya@bob', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Divya')")
    cursor.execute("INSERT INTO Customer VALUES (103, 'Karthik S', 'karthik@email.com', '9876500022', 'Chennai', '2002-07-20', 'hash_ghi789', 'karthik@bob', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Karthik')")

    # Seed Admins
    cursor.execute("INSERT INTO Admin VALUES (1, 'Abhimanyu', 'abhimanyu@bank.com', 'LoanOfficer')")
    cursor.execute("INSERT INTO Admin VALUES (2, 'Vinit Jangir', 'vinit.jangir@bank.com', 'BranchManager')")

    # Seed Loan Schemes
    cursor.execute("INSERT INTO LoanScheme VALUES ('Home Loan', 8.50)")
    cursor.execute("INSERT INTO LoanScheme VALUES ('Personal Loan', 12.00)")
    cursor.execute("INSERT INTO LoanScheme VALUES ('Education Loan', 7.25)")
    cursor.execute("INSERT INTO LoanScheme VALUES ('Vehicle Loan', 9.10)")

    # Seed Accounts
    cursor.execute("INSERT INTO Account (AccountNo, CustomerID, BranchCode, AccountType, Balance, OpenDate, Status, UpiPin) VALUES (5001, 101, 'BR01', 'Savings', 25000.0, '2024-01-18 10:00:00', 'Active', '1234')")
    cursor.execute("INSERT INTO Account (AccountNo, CustomerID, BranchCode, AccountType, Balance, OpenDate, Status, UpiPin) VALUES (5002, 102, 'BR02', 'Savings', 48000.0, '2024-02-15 11:30:00', 'Active', '1234')")
    cursor.execute("INSERT INTO Account (AccountNo, CustomerID, BranchCode, AccountType, Balance, OpenDate, Status, UpiPin) VALUES (5003, 103, 'BR01', 'Current', 12000.0, '2024-03-01 09:15:00', 'Active', '1234')")
    cursor.execute("INSERT INTO Account (AccountNo, CustomerID, BranchCode, AccountType, Balance, OpenDate, Status, UpiPin) VALUES (5004, 101, 'BR01', 'Current', 85000.0, '2024-04-10 14:00:00', 'Active', '1234')")

    # Seed Historical Transactions
    cursor.execute("INSERT INTO TransactionLog (TransactionID, AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef) VALUES (9001, 5001, 'Deposit', 5000.0, '2026-08-01 10:00:00', 'Salary credit', NULL, 'SAL20260801')")
    cursor.execute("INSERT INTO TransactionLog (TransactionID, AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef) VALUES (9002, 5001, 'Withdraw', 2000.0, '2026-08-05 14:20:00', 'ATM withdrawal', NULL, 'ATM88319201')")
    cursor.execute("INSERT INTO TransactionLog (TransactionID, AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef) VALUES (9003, 5001, 'Transfer', 3000.0, '2026-08-10 16:45:00', 'Transfer to Divya R', 5002, 'UPI77889102')")
    cursor.execute("INSERT INTO TransactionLog (TransactionID, AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef) VALUES (9004, 5002, 'Deposit', 3000.0, '2026-08-10 16:45:00', 'Received transfer from Sricharan', NULL, 'UPI77889102')")

    # Seed Loans
    cursor.execute("INSERT INTO Loan (LoanID, CustomerID, AdminID, LoanType, Amount, Status, ApplyDate, TenureMonths) VALUES (701, 101, 1, 'Home Loan', 1500000.0, 'Approved', '2026-06-01 10:00:00', 120)")
    cursor.execute("INSERT INTO Loan (LoanID, CustomerID, AdminID, LoanType, Amount, Status, ApplyDate, TenureMonths) VALUES (702, 102, NULL, 'Personal Loan', 200000.0, 'Pending', '2026-08-01 15:30:00', 36)")
    cursor.execute("INSERT INTO Loan (LoanID, CustomerID, AdminID, LoanType, Amount, Status, ApplyDate, TenureMonths) VALUES (703, 103, NULL, 'Education Loan', 450000.0, 'Pending', '2026-09-12 11:00:00', 48)")

    # Seed Beneficiaries
    cursor.execute("INSERT INTO Beneficiary (BeneficiaryID, CustomerID, BeneficiaryAccNo, BeneficiaryName, BankName, NickName) VALUES (301, 101, 5002, 'Divya R', 'Bank of Baroda', 'Divya')")
    cursor.execute("INSERT INTO Beneficiary (BeneficiaryID, CustomerID, BeneficiaryAccNo, BeneficiaryName, BankName, NickName) VALUES (302, 103, 999999, 'External Friend', 'Other Bank Ltd', 'College Friend')")
    cursor.execute("INSERT INTO Beneficiary (BeneficiaryID, CustomerID, BeneficiaryAccNo, BeneficiaryName, BankName, NickName) VALUES (303, 101, 5003, 'Karthik S', 'Bank of Baroda', 'Karthik S')")

    # SECTION 4: PL/SQL TRIGGERS (Installed to handle future web transactions dynamically)
    cursor.executescript("""
    CREATE TRIGGER trg_prevent_overdraft
    BEFORE INSERT ON TransactionLog
    FOR EACH ROW
    WHEN NEW.TxnType IN ('Withdraw', 'Transfer')
    BEGIN
        SELECT
            CASE
                WHEN (SELECT Balance FROM Account WHERE AccountNo = NEW.AccountNo) < NEW.Amount THEN
                    RAISE(ABORT, 'Insufficient balance for this operation (Overdraft Protection: ORA-20002)')
            END;
    END;

    CREATE TRIGGER trg_update_balance
    AFTER INSERT ON TransactionLog
    FOR EACH ROW
    BEGIN
        -- Deposit
        UPDATE Account
        SET Balance = Balance + NEW.Amount
        WHERE AccountNo = NEW.AccountNo AND NEW.TxnType = 'Deposit';

        -- Withdraw
        UPDATE Account
        SET Balance = Balance - NEW.Amount
        WHERE AccountNo = NEW.AccountNo AND NEW.TxnType = 'Withdraw';

        -- Transfer (Debit sender, credit receiver)
        UPDATE Account
        SET Balance = Balance - NEW.Amount
        WHERE AccountNo = NEW.AccountNo AND NEW.TxnType = 'Transfer';

        UPDATE Account
        SET Balance = Balance + NEW.Amount
        WHERE AccountNo = NEW.TargetAccountNo AND NEW.TxnType = 'Transfer';
    END;
    """)

    conn.commit()
    conn.close()
    print("Database fully initialized with BCNF schema, seed records, and PL/SQL triggers.")

# HELPER QUERIES (Corresponds to DA-2 Section 3, 4, 5, 6)
def get_total_balance(customer_id):
    """PL/SQL function get_total_balance equivalent"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(Balance), 0) FROM Account WHERE CustomerID = ?", (customer_id,))
    total = cur.fetchone()[0]
    conn.close()
    return total

def run_query_demonstrations():
    """Runs all 6 representative DA-2 queries and returns structured results"""
    conn = get_connection()
    cur = conn.cursor()
    results = {}

    # Q1: Selection
    cur.execute("SELECT AccountNo, Balance FROM Account WHERE AccountType = 'Savings' AND Status = 'Active'")
    results["Q1_SavingsAccounts"] = [dict(r) for r in cur.fetchall()]

    # Q2: Inner Join
    cur.execute("""
        SELECT C.Name, A.AccountNo, A.Balance 
        FROM Customer C 
        JOIN Account A ON C.CustomerID = A.CustomerID
    """)
    results["Q2_CustomerAccounts"] = [dict(r) for r in cur.fetchall()]

    # Q3: Aggregation
    cur.execute("SELECT BranchCode, SUM(Balance) AS TotalBalance FROM Account GROUP BY BranchCode")
    results["Q3_BranchBalances"] = [dict(r) for r in cur.fetchall()]

    # Q4: Subquery - Customers above average bank balance
    cur.execute("""
        SELECT C.Name, A.Balance 
        FROM Customer C 
        JOIN Account A ON C.CustomerID = A.CustomerID 
        WHERE A.Balance > (SELECT AVG(Balance) FROM Account)
    """)
    results["Q4_AboveAverageBalances"] = [dict(r) for r in cur.fetchall()]

    # Q5: Multi-table join with sort (Transaction history)
    cur.execute("""
        SELECT C.Name, T.TxnType, T.Amount, T.TxnDate, T.Description
        FROM TransactionLog T 
        JOIN Account A ON T.AccountNo = A.AccountNo 
        JOIN Customer C ON A.CustomerID = C.CustomerID 
        ORDER BY T.TxnDate DESC
    """)
    results["Q5_TransactionLedger"] = [dict(r) for r in cur.fetchall()]

    # Q6: Left Outer Join - Loans with applicant and approving admin
    cur.execute("""
        SELECT L.LoanID, C.Name AS Applicant, L.LoanType, L.Amount, L.Status, AD.Name AS ApprovedBy
        FROM Loan L 
        JOIN Customer C ON L.CustomerID = C.CustomerID 
        LEFT JOIN Admin AD ON L.AdminID = AD.AdminID
    """)
    results["Q6_LoansWithAdmins"] = [dict(r) for r in cur.fetchall()]

    conn.close()
    return results

if __name__ == "__main__":
    init_db()
