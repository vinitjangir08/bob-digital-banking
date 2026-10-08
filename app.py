"""
Bank of Baroda Next-Gen (BoB+ Digital Banking & UPI SuperApp)
Flask Backend API & Web Application
Integrates DA-2 Relational Architecture with Modern Fintech Innovations (GPay & Paytm)
"""

import os
import random
import string
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, render_template_string
import database

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = "bob-digital-banking-supersecret-key-2026"

# Current active session simulation (in-memory for demo / pair-programming)
CURRENT_SESSION = {
    "type": "customer",  # "customer" or "admin"
    "id": 101            # default to Sricharan K (101)
}

def generate_ref():
    return "BOB" + "".join(random.choices(string.digits, k=10))

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "BoB+ Digital Banking SuperApp", "time": datetime.now().isoformat()})

# ----------------- AUTH & PROFILES -----------------
@app.route("/api/users")
def get_all_users():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT CustomerID, Name, Email, Phone, UpiId, Avatar FROM Customer")
    customers = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT AdminID, Name, Email, Role FROM Admin")
    admins = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({
        "customers": customers,
        "admins": admins,
        "active_session": CURRENT_SESSION
    })

@app.route("/api/current_user")
def get_current_user():
    conn = database.get_connection()
    cur = conn.cursor()
    if CURRENT_SESSION["type"] == "customer":
        cur.execute("SELECT CustomerID, Name, Email, Phone, Address, DOB, UpiId, Avatar FROM Customer WHERE CustomerID = ?", (CURRENT_SESSION["id"],))
        user = cur.fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404
        user_dict = dict(user)
        user_dict["type"] = "customer"
        user_dict["total_balance"] = database.get_total_balance(CURRENT_SESSION["id"])
        conn.close()
        return jsonify(user_dict)
    else:
        cur.execute("SELECT AdminID, Name, Email, Role FROM Admin WHERE AdminID = ?", (CURRENT_SESSION["id"],))
        user = cur.fetchone()
        conn.close()
        if not user:
            return jsonify({"error": "Admin not found"}), 404
        user_dict = dict(user)
        user_dict["type"] = "admin"
        return jsonify(user_dict)

@app.route("/api/switch_user", methods=["POST"])
def switch_user():
    data = request.json or {}
    user_type = data.get("type", "customer")
    user_id = int(data.get("id", 101))
    CURRENT_SESSION["type"] = user_type
    CURRENT_SESSION["id"] = user_id
    return jsonify({"status": "switched", "active_session": CURRENT_SESSION})

# ----------------- ACCOUNTS -----------------
@app.route("/api/accounts")
def get_accounts():
    conn = database.get_connection()
    cur = conn.cursor()
    if CURRENT_SESSION["type"] == "customer":
        cur.execute("""
            SELECT A.AccountNo, A.CustomerID, A.BranchCode, A.AccountType, A.Balance, A.OpenDate, A.Status,
                   B.BranchName, B.BranchAddress
            FROM Account A
            JOIN Branch B ON A.BranchCode = B.BranchCode
            WHERE A.CustomerID = ?
            ORDER BY A.AccountNo ASC
        """, (CURRENT_SESSION["id"],))
    else:
        # Admin can view all bank accounts
        cur.execute("""
            SELECT A.AccountNo, A.CustomerID, A.BranchCode, A.AccountType, A.Balance, A.OpenDate, A.Status,
                   C.Name AS CustomerName, C.Email AS CustomerEmail, B.BranchName, B.BranchAddress
            FROM Account A
            JOIN Customer C ON A.CustomerID = C.CustomerID
            JOIN Branch B ON A.BranchCode = B.BranchCode
            ORDER BY A.AccountNo ASC
        """)
    accounts = [dict(r) for r in cur.fetchall()]
    total_balance = sum(a["Balance"] for a in accounts) if CURRENT_SESSION["type"] == "customer" else 0
    conn.close()
    return jsonify({
        "accounts": accounts,
        "total_balance": total_balance
    })

# ----------------- TRANSACTIONS & TRANSFERS -----------------
@app.route("/api/transactions")
def get_transactions():
    account_no = request.args.get("account_no", type=int)
    txn_type = request.args.get("txn_type")
    search = request.args.get("search", "").strip()
    limit = request.args.get("limit", 50, type=int)

    conn = database.get_connection()
    cur = conn.cursor()

    query = """
        SELECT T.TransactionID, T.AccountNo, T.TxnType, T.Amount, T.TxnDate, T.Description, T.TargetAccountNo, T.ReferenceRef,
               C.Name AS CustomerName, A.AccountType,
               TC.Name AS TargetCustomerName
        FROM TransactionLog T
        JOIN Account A ON T.AccountNo = A.AccountNo
        JOIN Customer C ON A.CustomerID = C.CustomerID
        LEFT JOIN Account TA ON T.TargetAccountNo = TA.AccountNo
        LEFT JOIN Customer TC ON TA.CustomerID = TC.CustomerID
        WHERE 1=1
    """
    params = []

    if CURRENT_SESSION["type"] == "customer":
        # Only transactions involving this customer's accounts
        query += " AND (A.CustomerID = ? OR TA.CustomerID = ?)"
        params.extend([CURRENT_SESSION["id"], CURRENT_SESSION["id"]])

    if account_no:
        query += " AND (T.AccountNo = ? OR T.TargetAccountNo = ?)"
        params.extend([account_no, account_no])

    if txn_type and txn_type != "All":
        query += " AND T.TxnType = ?"
        params.append(txn_type)

    if search:
        query += " AND (T.Description LIKE ? OR T.ReferenceRef LIKE ? OR TC.Name LIKE ?)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search, like_search])

    query += " ORDER BY T.TransactionID DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    txns = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(txns)

@app.route("/api/transactions/transfer", methods=["POST"])
def execute_transfer():
    data = request.json or {}
    source_acc = data.get("source_account_no")
    target_type = data.get("target_type", "account") # 'account', 'upi', 'phone', 'beneficiary'
    target_val = str(data.get("target_identifier", "")).strip()
    amount = float(data.get("amount", 0))
    pin = str(data.get("upi_pin", "")).strip()
    description = data.get("description", "Funds Transfer").strip() or "Transfer via BoB+ UPI"

    if amount <= 0:
        return jsonify({"error": "Transfer amount must be strictly greater than 0"}), 400

    conn = database.get_connection()
    cur = conn.cursor()

    try:
        # 1. Verify Source Account ownership and PIN
        cur.execute("SELECT AccountNo, CustomerID, Balance, UpiPin FROM Account WHERE AccountNo = ?", (source_acc,))
        source_row = cur.fetchone()
        if not source_row:
            return jsonify({"error": "Invalid source account"}), 400

        if CURRENT_SESSION["type"] == "customer" and source_row["CustomerID"] != CURRENT_SESSION["id"]:
            return jsonify({"error": "You do not own this account"}), 403

        # Default PIN is 1234
        if pin and pin != source_row["UpiPin"] and pin != "1234":
            return jsonify({"error": "Incorrect UPI/Transaction PIN. Authentication Failed."}), 401

        # 2. Resolve Target Account
        target_acc_no = None
        target_name = "Beneficiary"

        if target_type == "account":
            target_acc_no = int(target_val)
            cur.execute("SELECT A.AccountNo, C.Name FROM Account A JOIN Customer C ON A.CustomerID = C.CustomerID WHERE A.AccountNo = ?", (target_acc_no,))
            target_row = cur.fetchone()
            if not target_row:
                return jsonify({"error": f"Target Account #{target_acc_no} not found in bank network"}), 404
            target_name = target_row["Name"]

        elif target_type == "upi":
            cur.execute("SELECT CustomerID, Name FROM Customer WHERE LOWER(UpiId) = LOWER(?)", (target_val,))
            cust_row = cur.fetchone()
            if not cust_row:
                return jsonify({"error": f"UPI ID '{target_val}' not registered"}), 404
            target_name = cust_row["Name"]
            # Get their primary savings account
            cur.execute("SELECT AccountNo FROM Account WHERE CustomerID = ? ORDER BY AccountNo ASC LIMIT 1", (cust_row["CustomerID"],))
            acc_row = cur.fetchone()
            if not acc_row:
                return jsonify({"error": "Recipient has no active bank account"}), 400
            target_acc_no = acc_row["AccountNo"]

        elif target_type == "phone":
            cur.execute("SELECT CustomerID, Name FROM Customer WHERE Phone = ?", (target_val,))
            cust_row = cur.fetchone()
            if not cust_row:
                return jsonify({"error": f"Phone number '{target_val}' not linked to any BoB account"}), 404
            target_name = cust_row["Name"]
            cur.execute("SELECT AccountNo FROM Account WHERE CustomerID = ? ORDER BY AccountNo ASC LIMIT 1", (cust_row["CustomerID"],))
            acc_row = cur.fetchone()
            if not acc_row:
                return jsonify({"error": "Recipient has no active bank account"}), 400
            target_acc_no = acc_row["AccountNo"]

        elif target_type == "beneficiary":
            cur.execute("SELECT BeneficiaryAccNo, BeneficiaryName FROM Beneficiary WHERE BeneficiaryID = ?", (int(target_val),))
            ben_row = cur.fetchone()
            if not ben_row:
                return jsonify({"error": "Beneficiary record not found"}), 404
            target_acc_no = ben_row["BeneficiaryAccNo"]
            target_name = ben_row["BeneficiaryName"]

        if source_acc == target_acc_no:
            return jsonify({"error": "Source and destination account cannot be the same"}), 400

        ref_id = generate_ref()

        # 3. Insert into TransactionLog (Will automatically trigger trg_prevent_overdraft and trg_update_balance!)
        cur.execute("""
            INSERT INTO TransactionLog (AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef)
            VALUES (?, 'Transfer', ?, CURRENT_TIMESTAMP, ?, ?, ?)
        """, (source_acc, amount, f"{description} to {target_name}", target_acc_no, ref_id))

        # Check if target account is in our bank network; if so, create matching inbound credit record for receiver passbook
        cur.execute("SELECT CustomerID FROM Account WHERE AccountNo = ?", (target_acc_no,))
        in_network = cur.fetchone()
        if in_network:
            cur.execute("""
                INSERT INTO TransactionLog (AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef)
                VALUES (?, 'Deposit', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
            """, (target_acc_no, amount, f"UPI transfer received from A/C {source_acc}", ref_id))

        conn.commit()

        # Fetch updated balance
        cur.execute("SELECT Balance FROM Account WHERE AccountNo = ?", (source_acc,))
        new_balance = cur.fetchone()["Balance"]

        return jsonify({
            "status": "success",
            "message": f"₹{amount:,.2f} transferred successfully to {target_name}",
            "reference_id": ref_id,
            "amount": amount,
            "recipient": target_name,
            "target_account": target_acc_no,
            "source_account": source_acc,
            "new_balance": new_balance,
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "soundbox_text": f"Payment of rupees {int(amount)} received successfully on Bank of Baroda UPI"
        })

    except Exception as e:
        conn.rollback()
        err_msg = str(e)
        if "Insufficient balance" in err_msg or "ORA-20002" in err_msg:
            return jsonify({"error": "Insufficient funds in your account. Transaction declined by Overdraft Guard."}), 400
        return jsonify({"error": f"Transaction failed: {err_msg}"}), 400
    finally:
        conn.close()

@app.route("/api/transactions/deposit", methods=["POST"])
def deposit_funds():
    data = request.json or {}
    account_no = data.get("account_no")
    amount = float(data.get("amount", 0))
    description = data.get("description", "Instant Quick Deposit / Wallet Top-Up").strip()

    if amount <= 0:
        return jsonify({"error": "Deposit amount must be positive"}), 400

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        ref_id = generate_ref()
        cur.execute("""
            INSERT INTO TransactionLog (AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef)
            VALUES (?, 'Deposit', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
        """, (account_no, amount, description, ref_id))
        conn.commit()

        cur.execute("SELECT Balance FROM Account WHERE AccountNo = ?", (account_no,))
        new_balance = cur.fetchone()["Balance"]

        return jsonify({
            "status": "success",
            "message": f"₹{amount:,.2f} credited successfully to Account #{account_no}",
            "reference_id": ref_id,
            "new_balance": new_balance
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/transactions/withdraw", methods=["POST"])
def withdraw_funds():
    data = request.json or {}
    account_no = data.get("account_no")
    amount = float(data.get("amount", 0))
    description = data.get("description", "ATM Cash Withdrawal").strip()

    if amount <= 0:
        return jsonify({"error": "Withdrawal amount must be positive"}), 400

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        ref_id = generate_ref()
        cur.execute("""
            INSERT INTO TransactionLog (AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef)
            VALUES (?, 'Withdraw', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
        """, (account_no, amount, description, ref_id))
        conn.commit()

        cur.execute("SELECT Balance FROM Account WHERE AccountNo = ?", (account_no,))
        new_balance = cur.fetchone()["Balance"]

        return jsonify({
            "status": "success",
            "message": f"₹{amount:,.2f} withdrawn successfully from Account #{account_no}",
            "reference_id": ref_id,
            "new_balance": new_balance
        })
    except Exception as e:
        conn.rollback()
        err_msg = str(e)
        if "Insufficient balance" in err_msg or "ORA-20002" in err_msg:
            return jsonify({"error": "Insufficient account balance! Withdrawal aborted by Overdraft Protection."}), 400
        return jsonify({"error": err_msg}), 400
    finally:
        conn.close()

# ----------------- BENEFICIARIES -----------------
@app.route("/api/beneficiaries", methods=["GET", "POST"])
def beneficiaries_handler():
    conn = database.get_connection()
    cur = conn.cursor()

    if request.method == "GET":
        if CURRENT_SESSION["type"] == "customer":
            cur.execute("""
                SELECT B.BeneficiaryID, B.CustomerID, B.BeneficiaryAccNo, B.BeneficiaryName, B.BankName, B.NickName,
                       A.Balance AS TargetBalance, C.UpiId AS TargetUpi
                FROM Beneficiary B
                LEFT JOIN Account A ON B.BeneficiaryAccNo = A.AccountNo
                LEFT JOIN Customer C ON A.CustomerID = C.CustomerID
                WHERE B.CustomerID = ?
                ORDER BY B.BeneficiaryID DESC
            """, (CURRENT_SESSION["id"],))
        else:
            cur.execute("SELECT * FROM Beneficiary ORDER BY BeneficiaryID DESC")
        bens = [dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify(bens)

    elif request.method == "POST":
        data = request.json or {}
        acc_no = int(data.get("account_no", 0))
        name = data.get("name", "").strip()
        bank = data.get("bank", "Bank of Baroda").strip()
        nickname = data.get("nickname", "").strip() or name

        if not acc_no or not name:
            conn.close()
            return jsonify({"error": "Account number and Name are required"}), 400

        cur.execute("""
            INSERT INTO Beneficiary (CustomerID, BeneficiaryAccNo, BeneficiaryName, BankName, NickName)
            VALUES (?, ?, ?, ?, ?)
        """, (CURRENT_SESSION["id"], acc_no, name, bank, nickname))
        conn.commit()
        ben_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "success", "beneficiary_id": ben_id, "message": f"{name} added to saved beneficiaries"})

@app.route("/api/beneficiaries/<int:ben_id>", methods=["DELETE"])
def delete_beneficiary(ben_id):
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Beneficiary WHERE BeneficiaryID = ? AND CustomerID = ?", (ben_id, CURRENT_SESSION["id"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

# ----------------- LOANS & SCHEMES -----------------
@app.route("/api/loans")
def get_loans():
    conn = database.get_connection()
    cur = conn.cursor()

    # Loan Schemes
    cur.execute("SELECT LoanType, InterestRate FROM LoanScheme ORDER BY InterestRate ASC")
    schemes = [dict(r) for r in cur.fetchall()]

    # Loans for user or all
    if CURRENT_SESSION["type"] == "customer":
        cur.execute("""
            SELECT L.LoanID, L.CustomerID, L.AdminID, L.LoanType, L.Amount, L.Status, L.ApplyDate, L.TenureMonths,
                   S.InterestRate, AD.Name AS ApprovedBy
            FROM Loan L
            JOIN LoanScheme S ON L.LoanType = S.LoanType
            LEFT JOIN Admin AD ON L.AdminID = AD.AdminID
            WHERE L.CustomerID = ?
            ORDER BY L.LoanID DESC
        """, (CURRENT_SESSION["id"],))
    else:
        cur.execute("""
            SELECT L.LoanID, L.CustomerID, L.AdminID, L.LoanType, L.Amount, L.Status, L.ApplyDate, L.TenureMonths,
                   S.InterestRate, C.Name AS ApplicantName, C.Email AS ApplicantEmail, C.Phone AS ApplicantPhone,
                   AD.Name AS ApprovedBy
            FROM Loan L
            JOIN LoanScheme S ON L.LoanType = S.LoanType
            JOIN Customer C ON L.CustomerID = C.CustomerID
            LEFT JOIN Admin AD ON L.AdminID = AD.AdminID
            ORDER BY L.LoanID DESC
        """)
    loans = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({
        "schemes": schemes,
        "loans": loans
    })

@app.route("/api/loans/apply", methods=["POST"])
def apply_loan():
    data = request.json or {}
    loan_type = data.get("loan_type")
    amount = float(data.get("amount", 0))
    tenure = int(data.get("tenure_months", 24))

    if amount <= 0:
        return jsonify({"error": "Loan amount must be greater than zero"}), 400

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT InterestRate FROM LoanScheme WHERE LoanType = ?", (loan_type,))
        scheme = cur.fetchone()
        if not scheme:
            return jsonify({"error": f"Invalid loan scheme: {loan_type}"}), 400

        cur.execute("""
            INSERT INTO Loan (CustomerID, AdminID, LoanType, Amount, Status, ApplyDate, TenureMonths)
            VALUES (?, NULL, ?, ?, 'Pending', CURRENT_TIMESTAMP, ?)
        """, (CURRENT_SESSION["id"], loan_type, amount, tenure))
        conn.commit()
        loan_id = cur.lastrowid

        return jsonify({
            "status": "success",
            "loan_id": loan_id,
            "message": f"Loan application #{loan_id} for ₹{amount:,.2f} ({loan_type}) submitted for Admin approval."
        })
    finally:
        conn.close()

# ----------------- ADMIN PORTAL & LOAN ACTIONS -----------------
@app.route("/api/admin/loans/<int:loan_id>/action", methods=["POST"])
def admin_loan_action(loan_id):
    if CURRENT_SESSION["type"] != "admin":
        return jsonify({"error": "Unauthorized. Admin privileges required."}), 403

    data = request.json or {}
    action = data.get("action")  # 'approve' or 'reject'
    disburse_to_account = data.get("disburse", True)

    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT L.LoanID, L.CustomerID, L.Amount, L.Status, L.LoanType FROM Loan L WHERE L.LoanID = ?", (loan_id,))
        loan = cur.fetchone()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404

        if action == "approve":
            cur.execute("""
                UPDATE Loan
                SET Status = 'Approved', AdminID = ?
                WHERE LoanID = ?
            """, (CURRENT_SESSION["id"], loan_id))

            # Disburse loan amount directly into customer's primary savings account
            if disburse_to_account:
                cur.execute("SELECT AccountNo FROM Account WHERE CustomerID = ? AND AccountType = 'Savings' LIMIT 1", (loan["CustomerID"],))
                acc = cur.fetchone()
                if acc:
                    ref_id = generate_ref()
                    cur.execute("""
                        INSERT INTO TransactionLog (AccountNo, TxnType, Amount, TxnDate, Description, TargetAccountNo, ReferenceRef)
                        VALUES (?, 'Deposit', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
                    """, (acc["AccountNo"], loan["Amount"], f"Loan Disbursed (#{loan_id} {loan['LoanType']})", ref_id))

            conn.commit()
            return jsonify({"status": "success", "message": f"Loan #{loan_id} approved and funds disbursed successfully!"})

        elif action == "reject":
            cur.execute("""
                UPDATE Loan
                SET Status = 'Rejected', AdminID = ?
                WHERE LoanID = ?
            """, (CURRENT_SESSION["id"], loan_id))
            conn.commit()
            return jsonify({"status": "success", "message": f"Loan #{loan_id} rejected."})
        else:
            return jsonify({"error": "Invalid action. Use 'approve' or 'reject'"}), 400
    finally:
        conn.close()

@app.route("/api/admin/analytics")
def admin_analytics():
    conn = database.get_connection()
    cur = conn.cursor()

    # Branch Total Balances (DA-2 Q3)
    cur.execute("""
        SELECT B.BranchCode, B.BranchName, COALESCE(SUM(A.Balance), 0) AS TotalBalance, COUNT(A.AccountNo) AS TotalAccounts
        FROM Branch B
        LEFT JOIN Account A ON B.BranchCode = A.BranchCode
        GROUP BY B.BranchCode
    """)
    branch_stats = [dict(r) for r in cur.fetchall()]

    # Customers above average balance (DA-2 Q4)
    cur.execute("""
        SELECT C.CustomerID, C.Name, C.Email, A.AccountNo, A.Balance 
        FROM Customer C 
        JOIN Account A ON C.CustomerID = A.CustomerID 
        WHERE A.Balance > (SELECT AVG(Balance) FROM Account)
        ORDER BY A.Balance DESC
    """)
    vip_customers = [dict(r) for r in cur.fetchall()]

    # Overall Metrics
    cur.execute("SELECT COUNT(*) FROM Customer")
    total_customers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*), COALESCE(SUM(Balance), 0) FROM Account")
    acc_count, total_deposits = cur.fetchone()

    cur.execute("SELECT COUNT(*), COALESCE(SUM(Amount), 0) FROM Loan WHERE Status = 'Approved'")
    loan_count, total_loans = cur.fetchone()

    conn.close()
    return jsonify({
        "total_customers": total_customers,
        "total_accounts": acc_count,
        "total_deposits": total_deposits,
        "total_loans_disbursed": total_loans,
        "branch_stats": branch_stats,
        "vip_customers": vip_customers
    })

# ----------------- LIVE DB INSPECTOR & DA-2 QUERIES -----------------
@app.route("/api/db/inspect")
def inspect_database():
    conn = database.get_connection()
    cur = conn.cursor()

    tables = ["Branch", "Customer", "Admin", "LoanScheme", "Account", "TransactionLog", "Loan", "Beneficiary"]
    db_data = {}
    for t in tables:
        cur.execute(f"SELECT * FROM {t}")
        db_data[t] = [dict(r) for r in cur.fetchall()]

    conn.close()
    queries = database.run_query_demonstrations()

    return jsonify({
        "tables": db_data,
        "query_demonstrations": queries
    })

@app.route("/api/db/reset", methods=["POST"])
def reset_db():
    database.init_db()
    return jsonify({"status": "success", "message": "Database reset to initial enterprise state."})

# ----------------- FRONTEND UI ROUTE -----------------
@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting BoB+ Digital Banking Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
