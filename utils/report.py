import json
from datetime import datetime


def generate_json_report(data, filename):

    with open(filename, "w") as file:

        json.dump(data, file, indent=4)


def generate_txt_report(data, filename):

    with open(filename, "w") as file:

        file.write("PERSONAL DATA EXPOSURE REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write(
            f"Generated: {datetime.now()}\n\n"
        )

        file.write(
            f"Risk Level: {data['risk_level']}\n"
        )

        file.write(
            f"Risk Score: {data['risk_score']}/100\n\n"
        )

        file.write("Findings:\n")

        for finding in data["findings"]:

            file.write(f"- {finding}\n")