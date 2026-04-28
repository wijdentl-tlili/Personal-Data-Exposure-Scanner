def luhn_check(card_number: str):

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


def detect_card_type(card_number: str):

    if card_number.startswith("4"):
        return "Visa"

    if card_number.startswith(("51", "52", "53", "54", "55")):
        return "MasterCard"

    if card_number.startswith(("34", "37")):
        return "American Express"

    return "Unknown"


def scan_credit_card(card_number: str):

    valid = luhn_check(card_number)

    return {
        "valid": valid,
        "card_type": detect_card_type(card_number)
    }