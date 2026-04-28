import phonenumbers
from phonenumbers import geocoder, carrier


def scan_phone_number(phone: str):

    try:

        parsed = phonenumbers.parse(phone)

        if not phonenumbers.is_valid_number(parsed):
            return {
                "valid": False
            }

        return {
            "valid": True,
            "country": geocoder.description_for_number(parsed, "en"),
            "carrier": carrier.name_for_number(parsed, "en"),
            "international_format": phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        }

    except Exception:

        return {
            "valid": False
        }