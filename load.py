import pandas as pd
import sqlite3
import logging
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich import box
from config import DB_PATH, TABLE_NAME

logger = logging.getLogger(__name__)
console = Console()

def load(df):
    console.print(Panel.fit(
        "[bold green]💾 STAGE 4 — LOAD[/bold green]\n"
        "[green]Writing cleaned data to SQLite warehouse[/green]",
        border_style="green", box=box.DOUBLE
    ))
    df['date']        = df['date'].astype(str)
    df['day_of_week'] = df['day_of_week'].astype(str)
    df['is_anomaly']  = df['is_anomaly'].astype(int)

    CHUNK = 300
    total_chunks = (len(df) // CHUNK) + 1

    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[green]{task.description}"),
        BarColumn(bar_width=35, style="green", complete_style="bright_green"),
        TextColumn("[bright_green]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Writing chunks...", total=total_chunks)
        conn = sqlite3.connect(DB_PATH)
        first = True
        for i in range(0, len(df), CHUNK):
            chunk = df.iloc[i:i + CHUNK]
            chunk.to_sql(TABLE_NAME, conn,
                         if_exists='replace' if first else 'append',
                         index=False)
            first = False
            progress.advance(task)
            time.sleep(0.05)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS stock_summary AS
            SELECT
                ticker,
                COUNT(*)                        AS total_trading_days,
                ROUND(MIN(close),  2)           AS year_low,
                ROUND(MAX(close),  2)           AS year_high,
                ROUND(AVG(close),  2)           AS avg_close,
                ROUND(AVG(daily_return)*100, 4) AS avg_daily_return_pct,
                ROUND(AVG(volatility_20d), 4)   AS avg_volatility,
                ROUND(AVG(rsi_14), 2)           AS avg_rsi,
                SUM(is_anomaly)                 AS total_anomalies
            FROM stock_facts
            GROUP BY ticker
            ORDER BY avg_close DESC
        """)
        conn.commit()
        conn.close()

    console.print(
        f"\n  [bold bright_green]✓ LOAD COMPLETE[/bold bright_green]"
        f" — [green]{len(df):,} rows → [{TABLE_NAME}][/green]\n"
    )
    logger.info(f"LOAD | {len(df)} rows → {TABLE_NAME}")
