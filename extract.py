import yfinance as yf
import pandas as pd
import logging
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich import box
from config import STOCKS, START_DATE, END_DATE, LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

def extract():
    console.print(Panel.fit(
        "[bold yellow]⚡ STAGE 1 — EXTRACT[/bold yellow]\n"
        "[yellow]Pulling live market data from Yahoo Finance[/yellow]",
        border_style="yellow", box=box.DOUBLE
    ))
    all_frames = []
    with Progress(
        SpinnerColumn(style="yellow"),
        TextColumn("[yellow]{task.description}"),
        BarColumn(bar_width=35, style="yellow", complete_style="bright_yellow"),
        TextColumn("[bright_yellow]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Starting...", total=len(STOCKS))
        for ticker in STOCKS:
            progress.update(task, description=f"[yellow]Fetching [bold]{ticker}[/bold]...")
            time.sleep(0.3)
            try:
                raw = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
                if raw.empty:
                    console.print(f"  [yellow]No data for {ticker}[/yellow]")
                    continue
                if isinstance(raw.columns, pd.MultiIndex):
                    raw.columns = raw.columns.get_level_values(0)
                raw = raw.reset_index()
                raw.columns = [c.lower().replace(' ', '_') for c in raw.columns]
                raw['ticker'] = ticker
                raw['source'] = 'Yahoo Finance'
                all_frames.append(raw)
                logger.info(f"EXTRACT | {ticker} | {len(raw)} rows")
            except Exception as e:
                console.print(f"  [red]Failed {ticker}: {e}[/red]")
                logger.error(f"EXTRACT | {ticker} | FAILED | {e}")
            progress.advance(task)
    df = pd.concat(all_frames, ignore_index=True)
    console.print(
        f"\n  [bold bright_yellow]EXTRACT COMPLETE[/bold bright_yellow]"
        f" — [yellow]{len(df):,} rows | {df['ticker'].nunique()} stocks[/yellow]\n"
    )
    return df
