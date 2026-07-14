def detect_risk(df):

    risk = 0
    suspicious_accounts = []
    explanation = []

    # ---------------- Layering ----------------

    sender_counts = df.groupby("sender")["receiver"].nunique()
    max_receivers = sender_counts.max()

    suspicious_accounts = sender_counts[sender_counts >= 2].index.tolist()

    if max_receivers >= 10:
        points = 40
    elif max_receivers >= 5:
        points = 25
    elif max_receivers >= 2:
        points = 10
    else:
        points = 0

    if points:
        risk += points
        explanation.append({
            "factor": "One sender transferred to multiple receivers",
            "points": points
        })

    # ---------------- Banks ----------------

    banks = df["from_bank"].nunique()

    if banks >= 10:
        points = 30
    elif banks >= 5:
        points = 20
    elif banks >= 2:
        points = 10
    else:
        points = 0

    if points:
        risk += points
        explanation.append({
            "factor": "Transfers across multiple banks",
            "points": points
        })

    # ---------------- Similar Amounts ----------------

    std = df["amount"].std()

    if std < 100:
        points = 30
    elif std < 300:
        points = 20
    elif std < 500:
        points = 10
    else:
        points = 0

    if points:
        risk += points
        explanation.append({
            "factor": "Similar transaction amounts",
            "points": points
        })

    return min(risk,99), explanation, suspicious_accounts