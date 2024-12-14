import aiohttp
from typing import Dict, Tuple
import re
import json
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# This is expected to return a (kv) pair
async def fetch_decimal_denoms(is_mainnet: bool) -> Dict[str, int]:
    # default url
    request_url = (
        "https://sentry.lcd.injective.network/injective/exchange/v1beta1/exchange/denom_decimals"
        if is_mainnet
        else "https://testnet.lcd.injective.network/injective/exchange/v1beta1/exchange/denom_decimals"
    )

    logger.info(f"Fetching denoms from: {request_url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as response:
                if response.status != 200:
                    logger.error(f"Error status code: {response.status}")
                    logger.error(f"Error response: {await response.text()}")
                    return {}

                raw_data = await response.text()
                logger.info(f"Raw response: {raw_data}")

                denom_data = json.loads(raw_data)

                if "denom_decimals" not in denom_data:
                    logger.error("No 'denom_decimals' key in response")
                    logger.error(f"Response keys: {denom_data.keys()}")
                    return {}

                denom_data = denom_data["denom_decimals"]
                logger.info(f"Number of denoms found: {len(denom_data)}")

                response_dic: Dict[str, int] = {}
                for denom in denom_data:
                    response_dic[denom["denom"]] = int(denom["decimals"])
                    logger.info(
                        f"Added denom: {denom['denom']} with decimals: {denom['decimals']}"
                    )

                return response_dic

    except aiohttp.ClientError as e:
        logger.error(f"Network error occurred: {str(e)}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {}


def extract_market_info(market_id: str) -> Tuple[str, str, str]:
    """
    Extracts base currency, quote currency and market type from market identifier.

    :param market_id: Market identifier (e.g., 'btcusdt-perp', 'btcusdt', 'eth/usdt')
    :return: Tuple of (base_currency, quote_currency, market_type)
    """
    if not market_id:
        raise ValueError("Market ID cannot be empty")

    # Convert to lowercase and remove spaces
    market = market_id.lower().strip()

    # Check for perpetual market
    is_perp = bool(re.search(r"[/-]?perp(etual)?|futures?|swap", market, re.IGNORECASE))

    # Handle concatenated format with -perp suffix (e.g., btcusdt-perp)
    if is_perp:
        # Remove the perp suffix first
        market = re.sub(
            r"[/-]?(perp(etual)?|futures?|swap)[/-]?", "", market, re.IGNORECASE
        )

    # Handle different separator cases
    if "/" in market:
        parts = market.split("/")
    elif "-" in market:
        parts = market.split("-")
    else:
        # Handle concatenated format (e.g., btcusdt)
        if market.endswith("usdt"):
            parts = [market[:-4], "usdt"]
        elif market.endswith("inj"):
            parts = [market[:-3], "inj"]
        else:
            # If no known quote currency found, assume it's all base currency
            parts = [market, "usdt"]

    # Clean and validate parts
    if len(parts) < 2:
        parts.append("usdt")  # Default quote currency

    base = re.sub(r"[^a-zA-Z0-9]", "", parts[0]).upper()
    quote = re.sub(r"[^a-zA-Z0-9]", "", parts[1]).upper()

    if not re.match(r"^[A-Z0-9]{2,10}$", base):
        raise ValueError(f"Invalid base currency format: {base}")

    if not quote:
        quote = "USDT"

    market_type = "PERP" if is_perp else "SPOT"

    return base, quote, market_type


def normalize_ticker(ticker_symbol: str) -> str:
    """
    Normalizes various ticker formats to match the API's ticker format.
    Always uses USDT as quote currency.

    :param ticker_symbol: The ticker symbol to normalize (e.g., 'btc', 'eth', 'btc-perp')
    :return: The normalized ticker symbol (e.g., 'BTC/USDT PERP')
    """
    base, quote, market_type = extract_market_info(ticker_symbol)
    market_type = f" {market_type}" if market_type == "PERP" else ""
    return f"{base}/{quote}{market_type}"


async def get_market_id(ticker_symbol: str, network_type: str = "mainnet"):
    """
    Asynchronously fetches the market_id for a given ticker symbol from the Injective API.

    :param ticker_symbol: The ticker symbol to look up (e.g., 'BTCUSDT', 'btc-usdt', 'btc')
    :return: The market_id as a string if found, else None
    """
    # Normalize the ticker symbol to match the API format
    normalized_ticker = normalize_ticker(ticker_symbol)
    request_url = ""
    # API endpoint for derivative markets
    if network_type == "mainnet":
        request_url = "https://sentry.lcd.injective.network/injective/exchange/v1beta1/derivative/markets"
    else:
        request_url = "https://testnet.sentry.lcd.injective.network/injective/exchange/v1beta1/derivative/markets"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url) as response:
                data = await response.json()

                # Initialize a mapping of tickers to market IDs
                ticker_to_market_id = {}

                # Check if 'markets' key exists in the response
                if "markets" in data:
                    for market_info in data["markets"]:
                        market = market_info.get("market", {})
                        ticker = market.get("ticker", "").upper()
                        market_id = market.get("market_id")

                        # Ensure market_id does not have extra quotes
                        if isinstance(market_id, str):
                            market_id = market_id.strip("'\"")

                        if ticker and market_id:
                            ticker_to_market_id[ticker] = market_id

                    # Get the market_id for the normalized ticker
                    market_id = ticker_to_market_id.get(normalized_ticker)
                    if market_id:
                        return market_id
                    else:
                        print(f"No market ID found for ticker: {normalized_ticker}")
                else:
                    print("No market data found in the response.")
        except aiohttp.ClientError as e:
            print(f"HTTP request failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    return None
