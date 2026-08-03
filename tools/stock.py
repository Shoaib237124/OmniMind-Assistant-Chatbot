import yfinance as yf
from langchain_core.tools import tool
from pydantic import Field


@tool
def get_stock_price(
    symbol: str = Field(
        description="The stock ticker symbol, e.g., AAPL, MSFT, GOOGL, TSLA, NVDA"
    )
) -> str:
    """
    Get the latest stock price and daily statistics for a given stock ticker symbol.
    """
    try:
        # Sanitize symbol input
        clean_symbol = symbol.strip().upper()

        stock = yf.Ticker(clean_symbol)
        history = stock.history(period="2d")

        if history.empty:
            return f"No stock data found for ticker '{clean_symbol}'. Please verify the symbol."

        latest = history.iloc[-1]

        current_price = float(latest["Close"])
        high = float(latest["High"])
        low = float(latest["Low"])
        open_price = float(latest["Open"])

        return (
            f"Stock Ticker: {clean_symbol}\n"
            f"Current Price: ${current_price:.2f}\n"
            f"Open: ${open_price:.2f}\n"
            f"Day High: ${high:.2f}\n"
            f"Day Low: ${low:.2f}"
        )

    except Exception as e:
        return f"Error retrieving stock data for '{symbol}': {str(e)}"