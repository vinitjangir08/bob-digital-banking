import database

def test():
    database.init_db()
    conn = database.get_connection()
    cur = conn.cursor()

    # 1. Test Overdraft protection
    try:
        cur.execute("INSERT INTO TransactionLog (AccountNo, TxnType, Amount, Description) VALUES (5001, 'Withdraw', 999999, 'Big overdraft')")
        print("FAIL: Overdraft was not blocked!")
    except Exception as e:
        print("PASS Overdraft guard caught:", e)

    # 2. Test Balance update trigger
    cur.execute("SELECT Balance FROM Account WHERE AccountNo = 5001")
    b1_before = cur.fetchone()[0]
    cur.execute("SELECT Balance FROM Account WHERE AccountNo = 5002")
    b2_before = cur.fetchone()[0]
    print(f"Before Transfer: Account 5001 = {b1_before}, Account 5002 = {b2_before}")

    cur.execute("INSERT INTO TransactionLog (AccountNo, TxnType, Amount, Description, TargetAccountNo) VALUES (5001, 'Transfer', 1500, 'UPI Transfer', 5002)")
    conn.commit()

    cur.execute("SELECT Balance FROM Account WHERE AccountNo = 5001")
    b1_after = cur.fetchone()[0]
    cur.execute("SELECT Balance FROM Account WHERE AccountNo = 5002")
    b2_after = cur.fetchone()[0]
    print(f"After Transfer: Account 5001 = {b1_after}, Account 5002 = {b2_after}")
    assert b1_after == b1_before - 1500, "Debit failed"
    assert b2_after == b2_before + 1500, "Credit failed"
    print("PASS: Triggers verified perfectly!")

if __name__ == "__main__":
    test()
