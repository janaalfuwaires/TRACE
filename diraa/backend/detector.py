def detect_risk(df):

    risk = 0
    reasons = []
    suspicious_accounts = []

    sender_counts = df.groupby("sender")["receiver"].nunique()

    for sender, count in sender_counts.items():
        if count >= 2:
            suspicious_accounts.append(sender)

    if suspicious_accounts:
        risk += 40
        reasons.append("One sender transferred to multiple receivers")

    if df["from_bank"].nunique() > 2:
        risk += 30
        reasons.append("Transfers across multiple banks")

    if len(df) > 1 and df["amount"].std() < 200:
        risk += 20
        reasons.append("Similar transaction amounts")

    return min(risk, 99), reasons, suspicious_accounts