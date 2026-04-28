import typer
from rich.console import Console
from rich.table import Table
from rich import box

from utils.validators import (
    validate_email,
    validate_username,
    validate_phone,
    validate_credit_card,
)
from utils.report import generate_json_report, generate_txt_report, generate_html_report
from scanners.username_scanner import scan_username
from scanners.breach_scanner import scan_email_breach
from scanners.phone_scanner import scan_phone_number
from scanners.creditcard_scanner import scan_credit_card
from scanners.risk_engine import calculate_risk

app = typer.Typer()
console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bool_badge(value: bool, true_label="YES", false_label="NO") -> str:
    if value:
        return f"[green]{true_label}[/green]"
    return f"[red]{false_label}[/red]"


# ---------------------------------------------------------------------------
# Main command
# ---------------------------------------------------------------------------

@app.command()
def scan(
    email:    str = typer.Option(None, help="Email address to scan"),
    username: str = typer.Option(None, help="Username to scan"),
    phone:    str = typer.Option(None, help="Phone number (E.164 format, e.g. +21612345678)"),
    card:     str = typer.Option(None, help="Credit card number to analyze"),
):
    """Personal Data Exposure Scanner"""

    # Accumulators for risk engine
    breach_count     = 0
    username_hits    = 0
    phone_result     = None
    card_result      = None
    leaked_password  = False

    console.print("\n[bold cyan]━━━  Personal Data Exposure Scanner  ━━━[/bold cyan]\n")

    # ------------------------------------------------------------------ EMAIL
    if email:
        if not validate_email(email):
            console.print("[red][-][/red] Invalid email format — skipping.")
        else:
            console.print(f"[green][+][/green] Email accepted: [bold]{email}[/bold]")
            console.print("\n[bold cyan]Scanning breach databases…[/bold cyan]")

            breaches = scan_email_breach(email)
            breach_count = len(breaches)

            for b in breaches:
                if "Passwords" in b.get("data_exposed", []):
                    leaked_password = True

            if breaches:
                t = Table(title="Email Breach Results", box=box.ROUNDED)
                t.add_column("Breach",       style="red")
                t.add_column("Year",         style="yellow")
                t.add_column("Data Exposed", style="magenta")
                for b in breaches:
                    t.add_row(
                        b["breach"],
                        str(b["year"]),
                        ", ".join(b["data_exposed"]),
                    )
                console.print(t)
            else:
                console.print("[green][+][/green] No breaches found.\n")

    # --------------------------------------------------------------- USERNAME
    if username:
        if not validate_username(username):
            console.print("[red][-][/red] Invalid username — skipping.")
        else:
            console.print(f"[green][+][/green] Username accepted: [bold]{username}[/bold]")
            console.print("\n[bold cyan]Scanning username exposure…[/bold cyan]")

            results = scan_username(username)
            username_hits = sum(1 for r in results if r["found"])

            t = Table(title="Username Exposure", box=box.ROUNDED)
            t.add_column("Platform",    style="cyan")
            t.add_column("Found",       style="green")
            t.add_column("Profile URL", style="magenta")
            for r in results:
                t.add_row(
                    r["platform"],
                    bool_badge(r["found"]),
                    r["url"],
                )
            console.print(t)

    # ------------------------------------------------------------------ PHONE
    if phone:
        if not validate_phone(phone):
            console.print("[red][-][/red] Invalid phone number format — skipping.")
        else:
            console.print(f"\n[green][+][/green] Phone accepted: [bold]{phone}[/bold]")
            console.print("\n[bold cyan]Scanning phone number…[/bold cyan]")

            phone_result = scan_phone_number(phone)

            if not phone_result.get("valid"):
                console.print(
                    f"[red][-][/red] Phone lookup failed: "
                    f"{phone_result.get('error', 'unknown error')}"
                )
                phone_result = None
            else:
                t = Table(title="Phone Analysis", box=box.ROUNDED)
                t.add_column("Property", style="cyan")
                t.add_column("Value",    style="white")

                t.add_row("Country",              phone_result["country"])
                t.add_row("Region Code",           phone_result["region_code"])
                t.add_row("Carrier",               phone_result["carrier"] or "Unknown")
                t.add_row("Line Type",             phone_result["line_type"])
                t.add_row(
                    "VoIP / Virtual",
                    "[red]YES — higher risk[/red]" if phone_result["is_voip"]
                    else "[green]NO[/green]"
                )
                t.add_row("Timezones",             ", ".join(phone_result["timezones"]))
                t.add_row("International Format",  phone_result["international_format"])
                t.add_row("National Format",       phone_result["national_format"])
                t.add_row("E.164 Format",          phone_result["e164_format"])

                console.print(t)

    # ------------------------------------------------------------------- CARD
    if card:
        cleaned_card = card.replace(" ", "").replace("-", "")
        if not validate_credit_card(cleaned_card):
            console.print("[red][-][/red] Invalid credit card format — skipping.")
        else:
            console.print(f"\n[green][+][/green] Card format accepted.")
            console.print("\n[bold cyan]Analyzing credit card…[/bold cyan]")

            card_result = scan_credit_card(cleaned_card)
            bin_info    = card_result.get("bin_info", {})

            t = Table(title="Credit Card Analysis", box=box.ROUNDED)
            t.add_column("Property", style="cyan")
            t.add_column("Value",    style="white")

            t.add_row("Masked Number",  card_result["masked_number"])
            t.add_row("BIN (first 8)",  card_result["bin"])
            t.add_row("Network (local)", card_result["card_network"])
            t.add_row(
                "Luhn Valid",
                "[green]YES[/green]" if card_result["luhn_valid"] else "[red]NO[/red]"
            )

            if bin_info and "error" not in bin_info:
                t.add_row("Issuing Bank",   bin_info.get("bank_name", "Unknown"))
                t.add_row("Bank URL",       bin_info.get("bank_url", "N/A"))
                t.add_row("Card Scheme",    bin_info.get("card_scheme", "Unknown"))
                t.add_row("Card Type",      bin_info.get("card_type", "Unknown"))   # debit/credit
                t.add_row("Card Brand",     bin_info.get("card_brand", "Unknown"))  # Classic/Platinum
                t.add_row(
                    "Prepaid",
                    "[red]YES — higher risk[/red]" if bin_info.get("prepaid")
                    else "[green]NO[/green]"
                )
                t.add_row(
                    "Issuing Country",
                    f"{bin_info.get('country_emoji', '')} "
                    f"{bin_info.get('country_name', 'Unknown')} "
                    f"({bin_info.get('country_code', '?')})"
                )
                t.add_row("Currency",       bin_info.get("currency", "Unknown"))
            elif bin_info.get("error"):
                t.add_row("BIN Lookup",     f"[yellow]{bin_info['error']}[/yellow]")

            console.print(t)

    # --------------------------------------------------------------- RISK
    console.print("\n[bold cyan]Calculating risk score…[/bold cyan]\n")

    risk = calculate_risk(
        breach_count    = breach_count,
        username_hits   = username_hits,
        phone_result    = phone_result,
        card_result     = card_result,
        leaked_password = leaked_password,
    )

    level_color = risk.get("color", "white")
    t = Table(title="Risk Analysis", box=box.ROUNDED)
    t.add_column("Property", style="cyan")
    t.add_column("Value",    style="white")

    t.add_row("Risk Score", f"[bold]{risk['score']}/100[/bold]")
    t.add_row("Risk Level", f"[{level_color}]{risk['level']}[/{level_color}]")
    t.add_row("Findings",   "\n".join(risk["findings"]) if risk["findings"] else "None")

    console.print(t)
    console.print("\n[bold green]✓ Scan completed.[/bold green]")

    # --------------------------------------------------------------- REPORTS
    report_data = {
        "risk_score": risk["score"],
        "risk_level": risk["level"],
        "findings":   risk["findings"],
    }

    generate_json_report(report_data, "reports/report.json")
    generate_txt_report(report_data,  "reports/report.txt")
    generate_html_report(report_data,  "reports/report.html")
    console.print("[bold green][+][/bold green] Reports saved in /reports\n")


if __name__ == "__main__":
    app()