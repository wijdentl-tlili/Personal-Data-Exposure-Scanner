def calculate_risk(
    breach_count: int = 0,
    username_hits: int = 0,
    phone_result: dict = None,
    card_result: dict = None,
    leaked_password: bool = False,
) -> dict:
    """
    Calculate a composite risk score (0–100) based on scan results.

    Parameters
    ----------
    breach_count     : number of email breaches found
    username_hits    : number of platforms the username was found on
    phone_result     : full dict returned by scan_phone_number()
    card_result      : full dict returned by scan_credit_card()
    leaked_password  : whether a password was part of a breach
    """

    score = 0
    findings = []

    # ------------------------------------------------------------------
    # Email breaches
    # ------------------------------------------------------------------
    if breach_count > 0:
        added = min(breach_count * 20, 40)
        score += added
        findings.append(f"⚠  {breach_count} email breach(es) detected (+{added} pts)")

    if leaked_password:
        score += 40
        findings.append("🔑  Password exposed in a breach (+40 pts)")

    # ------------------------------------------------------------------
    # Username exposure
    # ------------------------------------------------------------------
    if username_hits > 0:
        added = min(username_hits * 5, 20)
        score += added
        findings.append(f"👤  Username found on {username_hits} platform(s) (+{added} pts)")

    # ------------------------------------------------------------------
    # Phone number
    # ------------------------------------------------------------------
    if phone_result and phone_result.get("valid"):
        base = 10
        score += base
        findings.append(f"📞  Valid phone number detected (+{base} pts)")

        if phone_result.get("is_voip"):
            score += 15
            findings.append("🔴  Phone is a VoIP/virtual number — higher anonymity risk (+15 pts)")

        line_type = phone_result.get("line_type", "")
        if line_type in ("Premium Rate", "Toll-Free"):
            score += 10
            findings.append(f"⚡  Phone line type is '{line_type}' — unusual (+10 pts)")

    # ------------------------------------------------------------------
    # Credit card
    # ------------------------------------------------------------------
    if card_result and card_result.get("luhn_valid"):
        base = 50
        score += base
        findings.append(f"💳  Luhn-valid credit card detected (+{base} pts)")

        bin_info = card_result.get("bin_info", {})

        if bin_info.get("prepaid"):
            score += 15
            findings.append("🔴  Card is prepaid — commonly used for anonymity (+15 pts)")

        card_type_lower = bin_info.get("card_type", "").lower()
        if card_type_lower == "debit":
            score += 5
            findings.append("ℹ   Card is a debit card (+5 pts)")

        country_code = bin_info.get("country_code", "")
        if country_code and country_code not in ("US", "GB", "FR", "DE", "CA", "AU"):
            score += 5
            findings.append(
                f"🌍  Card issued in {bin_info.get('country_name', country_code)} "
                f"— verify legitimacy (+5 pts)"
            )

    # ------------------------------------------------------------------
    # Risk level thresholds
    # ------------------------------------------------------------------
    final_score = min(score, 100)

    if final_score < 20:
        level, color = "LOW", "green"
    elif final_score < 50:
        level, color = "MEDIUM", "yellow"
    elif final_score < 80:
        level, color = "HIGH", "red"
    else:
        level, color = "CRITICAL", "bold red"

    return {
        "score": final_score,
        "level": level,
        "color": color,
        "findings": findings,
    }