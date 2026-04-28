def calculate_risk(
    breach_count=0,
    username_hits=0,
    phone_valid=False,
    card_valid=False,
    leaked_password=False
):

    score = 0
    findings = []

    # Email breaches
    if breach_count > 0:

        score += breach_count * 20

        findings.append(
            f"{breach_count} breach(es) detected"
        )

    # Password exposure
    if leaked_password:

        score += 40

        findings.append(
            "Password exposure detected"
        )

    # Username exposure
    if username_hits > 0:

        score += min(username_hits * 5, 20)

        findings.append(
            f"Username found on {username_hits} platform(s)"
        )

    # Phone exposure
    if phone_valid:

        score += 10

        findings.append(
            "Valid phone number detected"
        )

    # Credit card
    if card_valid:

        score += 50

        findings.append(
            "Valid credit card detected"
        )

    # Risk level
    if score < 20:
        level = "LOW"

    elif score < 50:
        level = "MEDIUM"

    elif score < 80:
        level = "HIGH"

    else:
        level = "CRITICAL"

    return {
        "score": min(score, 100),
        "level": level,
        "findings": findings
    }