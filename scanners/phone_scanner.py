import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from phonenumbers.phonenumberutil import number_type, PhoneNumberType


# Carriers that are typically VoIP providers
VOIP_KEYWORDS = [
    "google", "twilio", "vonage", "bandwidth", "magicjack",
    "skype", "ooma", "ringcentral", "dialpad", "grasshopper",
    "nextiva", "voip", "virtual", "internet"
]

LINE_TYPE_MAP = {
    PhoneNumberType.MOBILE: "Mobile",
    PhoneNumberType.FIXED_LINE: "Fixed Line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.TOLL_FREE: "Toll-Free",
    PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    PhoneNumberType.SHARED_COST: "Shared Cost",
    PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    PhoneNumberType.PAGER: "Pager",
    PhoneNumberType.UAN: "UAN",
    PhoneNumberType.UNKNOWN: "Unknown",
}


def detect_voip(carrier_name: str, line_type: PhoneNumberType) -> bool:
    """Heuristic VoIP detection based on carrier name and number type."""
    if line_type == PhoneNumberType.VOIP:
        return True
    carrier_lower = carrier_name.lower()
    return any(keyword in carrier_lower for keyword in VOIP_KEYWORDS)


def scan_phone_number(phone: str) -> dict:
    try:
        parsed = phonenumbers.parse(phone)

        if not phonenumbers.is_valid_number(parsed):
            return {"valid": False, "error": "Invalid phone number"}

        carrier_name = carrier.name_for_number(parsed, "en")
        country = geocoder.description_for_number(parsed, "en")
        timezones = list(timezone.time_zones_for_number(parsed))
        num_type = number_type(parsed)
        line_type_str = LINE_TYPE_MAP.get(num_type, "Unknown")
        is_voip = detect_voip(carrier_name, num_type)

        international_fmt = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        national_fmt = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        e164_fmt = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        # Region/country code
        region_code = phonenumbers.region_code_for_number(parsed)

        return {
            "valid": True,
            "country": country,
            "region_code": region_code,
            "carrier": carrier_name or "Unknown",
            "line_type": line_type_str,
            "is_voip": is_voip,
            "timezones": timezones,
            "international_format": international_fmt,
            "national_format": national_fmt,
            "e164_format": e164_fmt,
        }

    except phonenumbers.NumberParseException as e:
        return {"valid": False, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": f"Unexpected error: {str(e)}"}