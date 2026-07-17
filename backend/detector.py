def detect_risk(df):

    risk = 0
    suspicious_accounts = []
    explanation = []
    network_similarity = 0

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

    # ---------------- Multiple Banks ----------------

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
    return min(risk, 99), explanation, suspicious_accounts

def calculate_network_similarity(df, suspicious_accounts):

    results = []

    for account in suspicious_accounts:

        base_tx = df[df["sender"] == account]

        if len(base_tx) == 0:
            continue

        base_receivers = base_tx["receiver"].nunique()
        base_banks = base_tx["from_bank"].nunique()
        base_amount = base_tx["amount"].mean()
        base_payment = base_tx["payment_format"].mode()[0]

        linked_accounts = base_tx["receiver"].unique()

        for linked in linked_accounts:

            linked_tx = df[df["sender"] == linked]

            if len(linked_tx) == 0:
                continue

            score = 0

            # Number of receivers
            if abs(linked_tx["receiver"].nunique() - base_receivers) <= 2:
                score += 25

            # Banks used
            if abs(linked_tx["from_bank"].nunique() - base_banks) <= 1:
                score += 25

            # Average amount
            if abs(linked_tx["amount"].mean() - base_amount) <= base_amount * 0.2:
                score += 25

            # Payment method
            if linked_tx["payment_format"].mode()[0] == base_payment:
                score += 25

            
            if score >= 80:
                    risk_level = "🔴 High"
            elif score >= 50:
                    risk_level = "🟠 Medium"
            else:
                    risk_level = "🟢 Low"

            results.append({
                    "source": account,
                    "linked_account": linked,
                    "similarity": score,
                    "risk": risk_level
            })           

    return results