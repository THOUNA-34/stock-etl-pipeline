import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich import box

logger = logging.getLogger(__name__)
console = Console()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def transform(df):
    console.print(Panel.fit(
        "[bold magenta]⚙  STAGE 3 — TRANSFORM[/bold magenta]\n"
        "[magenta]Cleaning, enriching & engineering features[/magenta]",
        border_style="magenta", box=box.DOUBLE
    ))
    steps = [
        "Casting types & parsing dates",
        "Removing duplicates",
        "Handling missing values",
        "Computing 7-day moving average",
        "Computing 30-day moving average",
        "Computing RSI-14 indicator",
        "Calculating 20-day volatility",
        "Detecting price anomalies",
        "Engineering time features",
        "Adding audit timestamp",
    ]
    with Progress(
        SpinnerColumn(style="magenta"),
        TextColumn("[magenta]{task.description}"),
        BarColumn(bar_width=35, style="magenta", complete_style="bright_magenta"),
        TextColumn("[bright_magenta]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Transforming...", total=len(steps))

        progress.update(task, description=f"[magenta]{steps[0]}...")
        df['date']   = pd.to_datetime(df['date'],  errors='coerce')
        df['close']  = pd.to_numeric(df['close'],  errors='coerce')
        df['open']   = pd.to_numeric(df['open'],   errors='coerce')
        df['high']   = pd.to_numeric(df['high'],   errors='coerce')
        df['low']    = pd.to_numeric(df['low'],    errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[1]}...")
        df = df.drop_duplicates(subset=['date', 'ticker'])
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[2]}...")
        df = df.dropna(subset=['close', 'date'])
        df['volume'] = df['volume'].fillna(0)
        time.sleep(0.2); progress.advance(task)

        df = df.sort_values(['ticker', 'date'])

        progress.update(task, description=f"[magenta]{steps[3]}...")
        df['ma_7'] = df.groupby('ticker')['close'].transform(
            lambda x: x.rolling(7, min_periods=1).mean().round(4))
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[4]}...")
        df['ma_30'] = df.groupby('ticker')['close'].transform(
            lambda x: x.rolling(30, min_periods=1).mean().round(4))
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[5]}...")
        df['rsi_14'] = df.groupby('ticker')['close'].transform(
            lambda x: compute_rsi(x, 14)).round(2)
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[6]}...")
        df['volatility_20d'] = df.groupby('ticker')['close'].transform(
            lambda x: x.rolling(20, min_periods=1).std().round(4))
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[7]}...")
        df['price_zscore'] = df.groupby('ticker')['close'].transform(
            lambda x: ((x - x.rolling(30, min_periods=5).mean()) /
                       x.rolling(30, min_periods=5).std()).round(3))
        df['is_anomaly'] = (df['price_zscore'].abs() > 3).astype(int)
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[8]}...")
        df['year']         = df['date'].dt.year
        df['month']        = df['date'].dt.month
        df['quarter']      = df['date'].dt.quarter
        df['day_of_week']  = df['date'].dt.day_name()
        df['daily_return'] = df.groupby('ticker')['close'].pct_change().round(4)
        time.sleep(0.2); progress.advance(task)

        progress.update(task, description=f"[magenta]{steps[9]}...")
        df['etl_timestamp'] = str(datetime.utcnow())
        time.sleep(0.2); progress.advance(task)

    console.print(
        f"\n  [bold bright_magenta]✓ TRANSFORM COMPLETE[/bold bright_magenta]"
        f" — [magenta]{len(df):,} rows | {len(df.columns)} columns[/magenta]\n"
    )
    logger.info(f"TRANSFORM | {len(df)} rows | {len(df.columns)} cols")
    return df
