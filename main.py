import typer
from rich.console import Console
from rich.table import Table

from utils.validators import (
    validate_email,
    validate_username,
    validate_phone,
    validate_credit_card
)
from utils.report import (
    generate_json_report,
    generate_txt_report
)
from scanners.username_scanner import scan_username
from scanners.breach_scanner import scan_email_breach
from scanners.phone_scanner import scan_phone_number
from scanners.creditcard_scanner import scan_credit_card
from scanners.risk_engine import calculate_risk

app = typer.Typer()
console = Console()


@app.command()
def scan(
    email: str = typer.Option(None, help="Email address to scan"),
    username: str = typer.Option(None, help="Username to scan"),
    phone: str = typer.Option(None, help="Phone number to scan"),
    card: str = typer.Option(None, help="Credit card number to validate")
):
    """
    Personal Data Exposure Scanner
    """
    breach_count = 0
    username_hits = 0
    phone_valid = False
    card_valid = False
    leaked_password = False

    console.print("\n[bold cyan]Starting scan...[/bold cyan]\n")

    if email:
        if validate_email(email):
            console.print(f"[green][+][/green] Valid email: {email}")

            console.print("\n[bold cyan]Scanning breach databases...[/bold cyan]\n")

            breaches = scan_email_breach(email)
            if isinstance(breaches, list):

                breach_count = len(breaches)

                for breach in breaches:

                    exposed_data = breach.get(
                        "DataClasses",
                        []
                    )

                    if "Passwords" in exposed_data:
                        leaked_password = True

            if breaches:

                breach_table = Table(title="Breach Results")

                breach_table.add_column("Breach", style="red")
                breach_table.add_column("Year", style="yellow")
                breach_table.add_column("Data Exposed", style="magenta")

                for breach in breaches:

                    breach_table.add_row(
                        breach["breach"],
                        str(breach["year"]),
                        ", ".join(breach["data_exposed"])
                    )

                console.print(breach_table)

            else:
                console.print("[green][+][/green] No breaches found")
        else:
            console.print(f"[red][-][/red] Invalid email format")
            raise typer.Exit()

    if username:
        if validate_username(username):
            console.print(f"[green][+][/green] Valid username: {username}")

            console.print("\n[bold cyan]Scanning username exposure...[/bold cyan]\n")

            results = scan_username(username)
            username_hits = sum(
                        1 for result in results if result["found"]
                    )
            username_table = Table(title="Username Exposure Results")

            username_table.add_column("Platform", style="cyan")
            username_table.add_column("Found", style="green")
            username_table.add_column("Profile URL", style="magenta")

            for result in results:

                status = "[green]YES[/green]" if result["found"] else "[red]NO[/red]"

                username_table.add_row(
                    result["platform"],
                    status,
                    result["url"]
                )

            console.print(username_table)
        else:
            console.print(f"[red][-][/red] Invalid username")
            raise typer.Exit()
        
    if phone:

        if validate_phone(phone):
            phone_valid = True
            console.print(f"\n[green][+][/green] Valid phone number: {phone}")

            console.print("\n[bold cyan]Scanning phone number...[/bold cyan]\n")

            result = scan_phone_number(phone)

            phone_table = Table(title="Phone Scan Results")

            phone_table.add_column("Property", style="cyan")
            phone_table.add_column("Value", style="green")

            phone_table.add_row("Country", result["country"])
            phone_table.add_row("Carrier", result["carrier"])
            phone_table.add_row(
                "International Format",
                result["international_format"]
            )

            console.print(phone_table)

        else:
            console.print("[red][-][/red] Invalid phone number")


    if card:

        if validate_credit_card(card):
            card_valid = True
            console.print(f"\n[green][+][/green] Valid card format")

            console.print(
                "\n[bold cyan]Analyzing credit card...[/bold cyan]\n"
            )

            result = scan_credit_card(card)

            card_table = Table(title="Credit Card Analysis")

            card_table.add_column("Property", style="cyan")
            card_table.add_column("Value", style="green")

            card_table.add_row("Card Type", result["card_type"])
            card_table.add_row(
                "Luhn Valid",
                "YES" if result["valid"] else "NO"
            )

            masked = (
                "*" * (len(card) - 4)
            ) + card[-4:]

            card_table.add_row("Masked Number", masked)

            console.print(card_table)

        else:
            console.print("[red][-][/red] Invalid credit card format")

    table = Table(title="Scan Summary")

    table.add_column("Target", style="cyan")
    table.add_column("Status", style="green")

    if email:
        table.add_row(email, "Ready for breach scan")

    if username:
        table.add_row(username, "Ready for username scan")

    console.print(table)
    console.print(
        "\n[bold cyan]Calculating risk score...[/bold cyan]\n"
    )

    risk = calculate_risk(
        breach_count=breach_count,
        username_hits=username_hits,
        phone_valid=phone_valid,
        card_valid=card_valid,
        leaked_password=leaked_password
    )

    risk_table = Table(title="Risk Analysis")

    risk_table.add_column("Property", style="cyan")
    risk_table.add_column("Value", style="green")

    risk_table.add_row(
        "Risk Score",
        f"{risk['score']}/100"
    )

    risk_table.add_row(
        "Risk Level",
        risk["level"]
    )

    risk_table.add_row(
        "Findings",
        "\n".join(risk["findings"])
    )

    console.print(risk_table)
    console.print("\n[bold green]Scan completed.[/bold green]")
    report_data = {
        "risk_score": risk["score"],
        "risk_level": risk["level"],
        "findings": risk["findings"]
    }

    generate_json_report(
        report_data,
        "reports/report.json"
    )

    generate_txt_report(
        report_data,
        "reports/report.txt"
    )

    console.print(
        "\n[bold green][+][/bold green] Reports generated in /reports"
    )


if __name__ == "__main__":
    app()