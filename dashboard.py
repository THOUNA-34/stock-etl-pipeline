import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pyspark.sql import SparkSession
from rich.console import Console
from rich.panel import Panel
from rich import box

from config import TABLE_NAME, HTML_PATH, PNG_PATH, THEME_COLORS

console = Console()

spark = SparkSession.builder.getOrCreate()


def build_dashboard():

    console.print(
        Panel.fit(
            "[bold blue]📊 STAGE 5 — DASHBOARD[/bold blue]\n"
            "[blue]Generating interactive HTML + high-res PNG[/blue]",
            border_style="blue",
            box=box.DOUBLE,
        )
    )

    # Read Delta table
    df = spark.table(TABLE_NAME).toPandas()

    df["date"] = pd.to_datetime(df["date"])

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "📈 Closing Price & MA30",
            "📊 Daily Trading Volume",
            "⚡ RSI Indicator — 14 Day",
            "🌊 Price Volatility — 20 Day",
            "📅 Monthly Average Close",
            "🎯 Full Year Return (%)",
        ),
        vertical_spacing=0.13,
        horizontal_spacing=0.08,
    )

    for ticker in df["ticker"].unique():

        color = THEME_COLORS.get(ticker, "#FFFFFF")

        t = df[df["ticker"] == ticker].sort_values("date")

        fig.add_trace(
            go.Scatter(
                x=t["date"],
                y=t["close"],
                name=ticker,
                line=dict(color=color, width=2),
                legendgroup=ticker,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=t["date"],
                y=t["ma_30"],
                name=f"{ticker} MA30",
                line=dict(color=color, dash="dot"),
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                x=t["date"],
                y=t["volume"],
                marker_color=color,
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=t["date"],
                y=t["rsi_14"],
                line=dict(color=color),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=t["date"],
                y=t["volatility_20d"],
                fill="tozeroy",
                line=dict(color=color),
                showlegend=False,
            ),
            row=2,
            col=2,
        )

        monthly = t.groupby("month")["close"].mean().reset_index()

        fig.add_trace(
            go.Bar(
                x=monthly["month"],
                y=monthly["close"],
                marker_color=color,
                showlegend=False,
            ),
            row=3,
            col=1,
        )

        if len(t) > 1:
            ret = (
                (t["close"].iloc[-1] - t["close"].iloc[0])
                / t["close"].iloc[0]
                * 100
            )

            fig.add_trace(
                go.Bar(
                    x=[ticker],
                    y=[ret],
                    marker_color=color,
                    text=[f"{ret:.1f}%"],
                    textposition="outside",
                    showlegend=False,
                ),
                row=3,
                col=2,
            )

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="lime", row=2, col=1)

    fig.update_layout(
        title="🚀 STOCK MARKET ETL PIPELINE — ANALYTICS DASHBOARD",
        paper_bgcolor="#0A0E1A",
        plot_bgcolor="#0D1526",
        font=dict(color="white"),
        height=1100,
    )

    fig.write_html(HTML_PATH)

    console.print(f"[green]Dashboard saved → {HTML_PATH}[/green]")

    try:
        fig.write_image(PNG_PATH, width=1600, height=1100, scale=2)
    except Exception as e:
        console.print(f"[yellow]PNG skipped: {e}[/yellow]")

    console.print("\n[bold blue]✓ DASHBOARD COMPLETE[/bold blue]\n")
