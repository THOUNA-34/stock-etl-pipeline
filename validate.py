import pandas as pd
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from config import MAX_NULL_RATE, MIN_ROWS, STOCKS

logger = logging.getLogger(__name__)
console = Console()

def validate(df):
    console.print(Panel.fit(
        "[bold cyan]🔍 STAGE 2 — VALIDATE[/bold cyan]\n"
        "[cyan]Running automated data quality gate[/cyan]",
        border_style="cyan", box=box.DOUBLE
    ))
    checks = []
    passed_all = True

    ok = len(df) >= MIN_ROWS
    checks.append(("Minimum Row Count", f"{len(df):,}", f">= {MIN_ROWS}", ok))
    if not ok: passed_all = False

    for col in ['close', 'volume', 'ticker']:
        rate = df[col].isnull().mean()
        ok = rate <= MAX_NULL_RATE
        checks.append((f"Null Rate [{col}]", f"{rate*100:.2f}%", f"<= {MAX_NULL_RATE*100:.0f}%", ok))
        if not ok: passed_all = False

    neg = (df['close'] < 0).sum()
    ok = neg == 0
    checks.append(("Negative Prices", str(neg), "0", ok))
    if not ok: passed_all = False

    missing = set(STOCKS) - set(df['ticker'].unique())
    ok = len(missing) == 0
    checks.append(("All Tickers Present", str(set(df['ticker'].unique())), "All 5 stocks", ok))
    if not ok: passed_all = False

    table = Table(box=box.SIMPLE_HEAVY, border_style="cyan", header_style="bold cyan")
    table.add_column("Check", style="white", min_width=24)
    table.add_column("Actual", style="bright_white", justify="center")
    table.add_column("Required", style="cyan", justify="center")
    table.add_column("Status", justify="center")

    for name, actual, required, ok in checks:
        status = "[bold green]✓ PASS[/bold green]" if ok else "[bold red]✗ FAIL[/bold red]"
        table.add_row(name, actual, required, status)

    console.print(table)

    if passed_all:
        console.print("  [bold bright_cyan]✓ QUALITY GATE PASSED[/bold bright_cyan]\n")
        logger.info("VALIDATE | PASSED")
    else:
        console.print("  [bold red]✗ QUALITY GATE FAILED — Pipeline halted.[/bold red]\n")
        logger.error("VALIDATE | FAILED")
        raise ValueError("Quality gate failed. Fix issues and rerun.")

    return df
