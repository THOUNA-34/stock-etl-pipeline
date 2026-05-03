import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rich.console import Console
from rich.panel import Panel
from rich import box
from config import DB_PATH, TABLE_NAME, HTML_PATH, PNG_PATH, THEME_COLORS

console = Console()

def build_dashboard():
    console.print(Panel.fit(
        "[bold blue]📊 STAGE 5 — DASHBOARD[/bold blue]\n"
        "[blue]Generating interactive HTML + high-res PNG[/blue]",
        border_style="blue", box=box.DOUBLE
    ))
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "📈 Closing Price & MA30",
            "📊 Daily Trading Volume",
            "⚡ RSI Indicator — 14 Day",
            "🌊 Price Volatility — 20 Day",
            "📅 Monthly Average Close",
            "🎯 Full Year Return (%)"
        ),
        vertical_spacing=0.13,
        horizontal_spacing=0.08,
    )

    for ticker in df['ticker'].unique():
        color = THEME_COLORS.get(ticker, "#FFFFFF")
        t = df[df['ticker'] == ticker].sort_values('date')

        fig.add_trace(go.Scatter(
            x=t['date'], y=t['close'], name=ticker,
            line=dict(color=color, width=2),
            legendgroup=ticker, showlegend=True
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=t['date'], y=t['ma_30'], name=f"{ticker} MA30",
            line=dict(color=color, width=1, dash='dot'),
            legendgroup=ticker, showlegend=False, opacity=0.5
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=t['date'], y=t['volume'], name=ticker,
            marker_color=color, opacity=0.6,
            legendgroup=ticker, showlegend=False
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=t['date'], y=t['rsi_14'], name=ticker,
            line=dict(color=color, width=1.5),
            legendgroup=ticker, showlegend=False
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=t['date'], y=t['volatility_20d'], name=ticker,
            fill='tozeroy',
            line=dict(color=color, width=1.5),
            legendgroup=ticker, showlegend=False, opacity=0.7
        ), row=2, col=2)
        monthly = t.groupby('month')['close'].mean().reset_index()
        fig.add_trace(go.Bar(
            x=monthly['month'], y=monthly['close'].round(2),
            name=ticker, marker_color=color, opacity=0.85,
            legendgroup=ticker, showlegend=False
        ), row=3, col=1)
        if len(t) > 1:
            ret = ((t['close'].iloc[-1] - t['close'].iloc[0]) / t['close'].iloc[0] * 100)
            fig.add_trace(go.Bar(
                x=[ticker], y=[round(ret, 2)], name=ticker,
                marker_color=color, legendgroup=ticker, showlegend=False,
                text=[f"{ret:.1f}%"], textposition='outside',
                textfont=dict(color="white")
            ), row=3, col=2)

    fig.add_hline(y=70, line_dash="dash", line_color="red",
                  annotation_text="Overbought", annotation_font_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="lime",
                  annotation_text="Oversold", annotation_font_color="lime", row=2, col=1)

    fig.update_layout(
        title=dict(
            text="<b>🚀 STOCK MARKET ETL PIPELINE — ANALYTICS DASHBOARD</b>",
            font=dict(size=22, color="white"), x=0.5
        ),
        paper_bgcolor="#0A0E1A",
        plot_bgcolor="#0D1526",
        font=dict(color="white", family="Arial"),
        legend=dict(bgcolor="#1A2240", bordercolor="#2A3560",
                    borderwidth=1, font=dict(color="white", size=12)),
        height=1100,
    )
    fig.update_xaxes(gridcolor="#1A2240", zerolinecolor="#1A2240")
    fig.update_yaxes(gridcolor="#1A2240", zerolinecolor="#1A2240")

    fig.write_html(HTML_PATH)
    console.print(f"  [blue]✓ HTML → {HTML_PATH}[/blue]")

    try:
        fig.write_image(PNG_PATH, width=1600, height=1100, scale=2)
        console.print(f"  [blue]✓ PNG  → {PNG_PATH}[/blue]")
    except Exception as e:
        console.print(f"  [yellow]⚠ PNG skipped: {e}[/yellow]")

    console.print(f"\n  [bold bright_blue]✓ DASHBOARD COMPLETE[/bold bright_blue]\n")
