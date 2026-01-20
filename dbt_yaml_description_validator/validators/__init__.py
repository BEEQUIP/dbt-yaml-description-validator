__version__ = "0.0.1"

from . import article, capital, period, symbol, spaces

RULES = {
    "article": article,
    "capital": capital,
    "period": period,
    "symbols": symbol,
    "spaces": spaces
}
