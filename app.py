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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import zlib
import base64

BUNDLED_HTML = """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"""
BUNDLED_JS = """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"""

def ensure_frontend_assets(tpl_dir, st_dir):
    try:
        os.makedirs(tpl_dir, exist_ok=True)
        os.makedirs(st_dir, exist_ok=True)
        idx = os.path.join(tpl_dir, "index.html")
        js = os.path.join(st_dir, "app.js")
        if not os.path.isfile(idx) or os.path.getsize(idx) == 0:
            with open(idx, "wb") as f:
                f.write(zlib.decompress(base64.b64decode(BUNDLED_HTML)))
        if not os.path.isfile(js) or os.path.getsize(js) == 0:
            with open(js, "wb") as f:
                f.write(zlib.decompress(base64.b64decode(BUNDLED_JS)))
    except Exception as e:
        print("Warning unpacking frontend assets:", e)

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ensure_frontend_assets(TEMPLATES_DIR, STATIC_DIR)


app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
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
@app.route("/index.html")
def index():
    # 1. Try render_template
    try:
        from flask import render_template
        return render_template("index.html")
    except Exception:
        pass

    # 2. Try send_from_directory with absolute TEMPLATES_DIR
    try:
        return send_from_directory(TEMPLATES_DIR, "index.html")
    except Exception:
        pass

    # 3. Direct multi-location file read fallback
    for p in [
        os.path.join(TEMPLATES_DIR, "index.html"),
        os.path.join(BASE_DIR, "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html"),
        os.path.join(BASE_DIR, "bob-digital-banking", "templates", "index.html"),
        os.path.join(os.getcwd(), "bob-digital-banking", "templates", "index.html")
    ]:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}

    return f"Template index.html not found. CWD: {os.getcwd()}, BASE_DIR: {BASE_DIR}", 404

@app.route("/static/<path:filename>")
def serve_static(filename):
    for d in [
        STATIC_DIR,
        os.path.join(BASE_DIR, "static"),
        os.path.join(os.getcwd(), "static"),
        os.path.join(BASE_DIR, "bob-digital-banking", "static"),
        os.path.join(os.getcwd(), "bob-digital-banking", "static")
    ]:
        target = os.path.join(d, filename)
        if os.path.isfile(target):
            return send_from_directory(d, filename)
    return "Static file not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting BoB+ Digital Banking Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
