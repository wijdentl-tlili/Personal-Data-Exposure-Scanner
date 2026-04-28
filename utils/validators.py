import re


def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.-]{3,30}$'
    return re.match(pattern, username) is not None