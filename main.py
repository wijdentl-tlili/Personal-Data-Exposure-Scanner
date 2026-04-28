import typer
from rich.console import Console
from rich.table import Table

from utils.validators import validate_email, validate_username

app = typer.Typer()
console = Console()


@app.command()
def scan(
    email: str = typer.Option(None, help="Email address to scan"),
    username: str = typer.Option(None, help="Username to scan")
):
    """
    Personal Data Exposure Scanner
    """

    console.print("\n[bold cyan]Starting scan...[/bold cyan]\n")

    if email:
        if validate_email(email):
            console.print(f"[green][+][/green] Valid email: {email}")
        else:
            console.print(f"[red][-][/red] Invalid email format")
            raise typer.Exit()

    if username:
        if validate_username(username):
            console.print(f"[green][+][/green] Valid username: {username}")
        else:
            console.print(f"[red][-][/red] Invalid username")
            raise typer.Exit()

    table = Table(title="Scan Summary")

    table.add_column("Target", style="cyan")
    table.add_column("Status", style="green")

    if email:
        table.add_row(email, "Ready for breach scan")

    if username:
        table.add_row(username, "Ready for username scan")

    console.print(table)

    console.print("\n[bold green]Scan completed.[/bold green]")


if __name__ == "__main__":
    app()