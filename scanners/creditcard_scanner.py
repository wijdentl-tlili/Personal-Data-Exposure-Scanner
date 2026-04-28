import httpx
import re


# ---------------------------------------------------------------------------
# Luhn algorithm
# ---------------------------------------------------------------------------

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    odd = False
    for digit in reversed(digits):
        if odd:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
        odd = not odd
    return checksum % 10 == 0


# ---------------------------------------------------------------------------
# Card network detection (extended)
# ---------------------------------------------------------------------------

CARD_PATTERNS = [
    ("Visa",             r"^4\d{12,18}$"),
    ("MasterCard",       r"^5[1-5]\d{14}$|^2(2[2-9][1-9]|[3-6]\d{2}|7[01]\d|720)\d{12}$"),
    ("American Express", r"^3[47]\d{13}$"),
    ("Discover",         r"^6(?:011|22(?:1(?:2[6-9]|[3-9]\d)|[2-8]\d{2}|9(?:[01]\d|2[0-5]))|4[4-9]\d|5\d{2})\d{10}$"),
    ("JCB",              r"^(?:2131|1800|35\d{3})\d{11}$"),
    ("Diners Club",      r"^3(?:0[0-5]|[68]\d)\d{11}$"),
    ("UnionPay",         r"^62\d{14,17}$"),
    ("Maestro",          r"^(?:5018|5020|5038|6304|6759|6761|6763)\d{8,15}$"),
]


def detect_card_type(card_number: str) -> str:
    cleaned = re.sub(r"[\s\-]", "", card_number)
    for name, pattern in CARD_PATTERNS:
        if re.match(pattern, cleaned):
            return name
    return "Unknown"


# ---------------------------------------------------------------------------
# BIN (Bank Identification Number) lookup
# Uses binlist.net — free, no API key required
# ---------------------------------------------------------------------------

def lookup_bin(card_number: str) -> dict:
    """
    Query binlist.net for the first 8 digits of the card.
    Returns enriched info or an empty dict on failure.
    """
    cleaned = re.sub(r"[\s\-]", "", card_number)
    bin_digits = cleaned[:8]  # 8-digit BIN for best accuracy

    try:
        response = httpx.get(
            f"https://lookup.binlist.net/{bin_digits}",
            headers={"Accept-Version": "3"},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "bank_name":    data.get("bank", {}).get("name", "Unknown"),
                "bank_url":     data.get("bank", {}).get("url", ""),
                "bank_phone":   data.get("bank", {}).get("phone", ""),
                "card_scheme":  data.get("scheme", "Unknown").title(),
                "card_type":    data.get("type", "Unknown").title(),      # debit / credit
                "card_brand":   data.get("brand", "Unknown"),             # Visa Classic, Platinum…
                "prepaid":      data.get("prepaid", False),
                "country_name": data.get("country", {}).get("name", "Unknown"),
                "country_code": data.get("country", {}).get("alpha2", "??"),
                "country_emoji":data.get("country", {}).get("emoji", ""),
                "currency":     data.get("country", {}).get("currency", "Unknown"),
            }
        else:
            return {"error": f"BIN lookup returned HTTP {response.status_code}"}

    except httpx.TimeoutException:
        return {"error": "BIN lookup timed out"}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def mask_card(card_number: str) -> str:
    cleaned = re.sub(r"[\s\-]", "", card_number)
    return "*" * (len(cleaned) - 4) + cleaned[-4:]


def scan_credit_card(card_number: str) -> dict:
    cleaned = re.sub(r"[\s\-]", "", card_number)

    luhn_valid = luhn_check(cleaned)
    card_type  = detect_card_type(cleaned)
    masked     = mask_card(cleaned)

    result = {
        "luhn_valid": luhn_valid,
        "card_network": card_type,
        "masked_number": masked,
        "bin": cleaned[:8],
    }

    # Only do BIN lookup if Luhn passes (avoid wasting requests on garbage input)
    if luhn_valid:
        bin_info = lookup_bin(cleaned)
        result["bin_info"] = bin_info
    else:
        result["bin_info"] = {}

    return result