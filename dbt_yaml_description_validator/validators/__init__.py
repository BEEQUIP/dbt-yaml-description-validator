__version__ = "0.0.1"

from dbt_yaml_description_validator.validators import article, capital, dot, symbol

RULES = {
    "article": article,
    "capital": capital,
    "dot": dot,
    "symbols": symbol,
}