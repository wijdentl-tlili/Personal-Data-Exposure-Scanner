import json


BREACH_DB = "data/breaches.json"


def scan_email_breach(email: str):

    try:
        with open(BREACH_DB, "r") as file:
            breaches = json.load(file)

    except Exception:
        return []

    results = []

    for breach in breaches:

        if breach["email"].lower() == email.lower():

            results.append({
                "breach": breach["breach"],
                "year": breach["year"],
                "data_exposed": breach["data_exposed"]
            })

    return results