import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich import box

from extract   import extract
from validate  import validate
from transform import transform
from load      import load
from dashboard import build_dashboard

console = Console()

def main():
    console.print()
    console.print(Panel(
        "[bold white]🚀  STOCK MARKET ETL PIPELINE  v1.0[/bold white]\n"
        "[dim white]AAPL · GOOGL · TSLA · MSFT · AMZN  |  Full Year 2024[/dim white]",
        border_style="bright_white",
        box=box.DOUBLE_EDGE,
        padding=(1, 8),
    ))
    console.print()

    start = time.time()

    df_raw       = extract()
    df_validated = validate(df_raw)
    df_clean     = transform(df_validated)
    load(df_clean)
    build_dashboard()

    elapsed = round(time.time() - start, 2)

    console.print(Rule("[bold white]✅  PIPELINE SUMMARY[/bold white]"))
    console.print()

    summary = Table(box=box.SIMPLE_HEAVY, border_style="bright_white",
                    show_header=False, padding=(0, 3))
    summary.add_column(style="dim white", min_width=22)
    summary.add_column(style="bold white")

    summary.add_row("Status",               "[bold green]✅ SUCCESS[/bold green]")
    summary.add_row("Stocks Tracked",       str(df_clean['ticker'].nunique()))
    summary.add_row("Total Records",        f"{len(df_clean):,} rows")
    summary.add_row("Features Engineered",  f"{len(df_clean.columns)} columns")
    summary.add_row("Anomalies Detected",   str(df_clean['is_anomaly'].sum()))
    summary.add_row("Pipeline Runtime",     f"{elapsed}s")
    summary.add_row("Database",             "[cyan]output/stock_warehouse.db[/cyan]")
    summary.add_row("Interactive Dashboard","[cyan]output/dashboard.html[/cyan]")
    summary.add_row("Chart PNG",            "[cyan]output/dashboard.png[/cyan]")
    summary.add_row("Log File",             "[cyan]logs/pipeline.log[/cyan]")

    console.print(summary)
    console.print()

if __name__ == "__main__":
    main()
