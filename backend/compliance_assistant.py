"""
AI Compliance Assistant for TRACE.
Rule-based only — no external LLM calls.
Consumes the output of detector.detect_risk() and produces
per-account explanations + recommended actions.
"""
import pandas as pd  # placed after function for clarity; move to top in file
from datetime import datetime


def _account_stats(df, account):
    """Pull the behavioral stats for one account from the transactions df."""
    sent = df[df["sender"] == account]
    received = df[df["receiver"] == account]

    return {
        "sent_count": len(sent),
        "received_count": len(received),
        "unique_receivers": sent["receiver"].nunique(),
        "unique_senders": received["sender"].nunique(),
        "total_sent": float(sent["amount"].sum()),
        "total_received": float(received["amount"].sum()),
        "banks_used": pd.concat([sent["from_bank"], received["to_bank"]]).nunique()
        if len(sent) + len(received) > 0 else 0,
        "amount_std": float(sent["amount"].std()) if len(sent) > 1 else 0.0,
    }





def explain_account(df, account, global_reasons):
    """
    Build a human-readable explanation for why this specific account
    was flagged, based on its own transaction pattern plus the
    global reasons detector.py already found for the batch.
    """
    stats = _account_stats(df, account)
    explanations = []

    if stats["unique_receivers"] >= 2:
        explanations.append(
            f"This account sent funds to {stats['unique_receivers']} different "
            f"receivers across {stats['sent_count']} transaction(s), a pattern "
            f"consistent with fund distribution or layering."
        )

    if "Transfers across multiple banks" in global_reasons and stats["banks_used"] > 2:
        explanations.append(
            f"Involved in transactions spanning {stats['banks_used']} different "
            f"banks, increasing difficulty of tracing fund origin."
        )

    if "Similar transaction amounts" in global_reasons and stats["amount_std"] < 200 and stats["sent_count"] > 1:
        explanations.append(
            "Outgoing transaction amounts are unusually consistent in size, "
            "a pattern often associated with structuring to avoid detection thresholds."
        )

    if stats["total_sent"] > 0 and stats["unique_receivers"] >= 3:
        explanations.append(
            f"Total outgoing volume of {stats['total_sent']:.2f} distributed "
            f"across multiple counterparties suggests possible fund dispersal."
        )

    if not explanations:
        explanations.append(
            "Flagged by the detection engine as part of a suspicious sender "
            "pattern in this batch; no additional account-specific anomaly "
            "was isolated."
        )

    return explanations, stats


def recommend_action(risk_score, stats):
    """
    Rule-based recommendation using the batch risk_score (from detector.py)
    combined with this account's own behavioral stats.
    """
    if risk_score >= 80 and stats["unique_receivers"] >= 3:
        return {
            "action": "Escalate Investigation",
            "urgency": "Critical",
            "reason": "High batch risk score combined with a wide fund-distribution "
                       "pattern from this account requires immediate escalation "
                       "to a senior compliance officer.",
        }
    elif risk_score >= 70:
        return {
            "action": "Freeze Account",
            "urgency": "High",
            "reason": "Overall risk score exceeds the threshold for continued "
                       "unrestricted activity. Recommend freezing pending review.",
        }
    elif risk_score >= 40:
        return {
            "action": "Request Enhanced Due Diligence",
            "urgency": "Medium",
            "reason": "Risk indicators are elevated. Recommend verifying source "
                       "of funds and account ownership before further action.",
        }
    else:
        return {
            "action": "Continue Monitoring",
            "urgency": "Low",
            "reason": "Risk indicators are present but below intervention "
                       "threshold. Recommend continued automated monitoring.",
        }


def generate_compliance_report(df, risk_score, reasons, suspicious_accounts):
    """
    Main entry point. Returns a dict with a narrative summary and
    a per-account breakdown, ready to be sent as JSON or rendered in Streamlit.
    """
    account_reports = []

    for account in suspicious_accounts:
        explanations, stats = explain_account(df, account, reasons)
        rec = recommend_action(risk_score, stats)
        account_reports.append({
            "account_id": account,
            "explanations": explanations,
            "stats": stats,
            "action": rec["action"],
            "urgency": rec["urgency"],
            "action_reason": rec["reason"],
        })

    action_counts = {}
    for r in account_reports:
        action_counts[r["action"]] = action_counts.get(r["action"], 0) + 1

    summary_lines = [
        f"Compliance Analysis Summary — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"{len(account_reports)} account(s) were flagged as suspicious, "
        f"with an overall batch risk score of {risk_score}%.",
        f"Detected pattern(s): {', '.join(reasons) if reasons else 'none'}.",
        "",
        "Recommended actions breakdown:",
    ]
    for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
        summary_lines.append(f"  • {action}: {count} account(s)")

    summary_lines += [
        "",
        "This report was generated automatically by TRACE's rule-based "
        "compliance engine and should be reviewed by a qualified AML officer "
        "before final action is taken.",
    ]

    return {
        "summary": "\n".join(summary_lines),
        "accounts": account_reports,
    }