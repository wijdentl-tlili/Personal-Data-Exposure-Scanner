import re
import phonenumbers


def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.-]{3,30}$'
    return re.match(pattern, username) is not None


def validate_phone(phone: str) -> bool:

    try:

        parsed = phonenumbers.parse(phone)

        return phonenumbers.is_valid_number(parsed)

    except Exception:
        return False


def validate_credit_card(card_number: str) -> bool:

    pattern = r'^[0-9]{13,19}$'

    cleaned = card_number.replace(" ", "").replace("-", "")

    return re.match(pattern, cleaned) is not None