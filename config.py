STOCKS     = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]
START_DATE = "2024-01-01"
END_DATE   = "2024-12-31"

DB_PATH    = "output/stock_warehouse.db"
TABLE_NAME = "stock_facts"
LOG_FILE   = "logs/pipeline.log"
PNG_PATH   = "output/dashboard.png"
HTML_PATH  = "output/dashboard.html"

MAX_NULL_RATE = 0.02
MIN_ROWS      = 100

THEME_COLORS = {
    "AAPL":  "#FF6B6B",
    "GOOGL": "#FFD93D",
    "TSLA":  "#6BCB77",
    "MSFT":  "#4D96FF",
    "AMZN":  "#FF922B",
}
