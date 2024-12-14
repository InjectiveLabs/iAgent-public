from typing import Dict, List
import json
import re
import base64
import requests
from injective_functions.utils.indexer_requests import get_market_id


def base64convert(s):
    try:
        int(s.replace("0x", ""), 16)
        return ("0x" + s).upper()
    except:
        # If not hex, convert base64 to hex with 0x
        return "0x" + base64.b64decode(s).hex().upper()


def get_bridge_fee() -> float:
    asset = "injective-protocol"
    coingecko_endpoint = (
        f"https://api.coingecko.com/api/v3/simple/price?ids={asset}&vs_currencies=usd"
    )
    token_price = requests.get(coingecko_endpoint).json()[asset]["usd"]
    minimum_bridge_fee_usd = 10
    return float(minimum_bridge_fee_usd / token_price)


# TODO: validate this properly and assert type safety here
def validate_market_id(market_id: str = None) -> bool:
    str_id = str(market_id).lower()

    if (str_id[:2] == "0x" and len(str_id) == 66) or (len(str(market_id)) == 64):
        return True
    else:
        return False


def combine_function_schemas(input_files: List[str]) -> Dict:
    # Initialize combined data structure
    combined_data = {"functions": []}
    # Read and combine all input files
    for file_path in input_files:
        try:
            print(file_path)
            with open(file_path, "r") as file:
                data = json.load(file)
                if "functions" in data:
                    combined_data["functions"].extend(data["functions"])
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found, skipping...")
        except json.JSONDecodeError:
            print(f"Warning: File {file_path} contains invalid JSON, skipping...")

    output_file = "./injective_functions/functions_schemas.json"
    # Write combined data to output file
    with open(output_file, "w") as file:
        json.dump(combined_data, file, indent=2)
    return combined_data


async def impute_market_ids(market_ids):
    lst = []
    for market_id in market_ids:
        if validate_market_id(market_id):
            lst.append(market_id)
        else:
            lst.append(await get_market_id(market_id))
    return lst


async def impute_market_id(market_id):
    if validate_market_id(market_id):
        return market_id
    else:
        return await get_market_id(market_id)


def detailed_exception_info(e) -> Dict:
    return {
        "success": False,
        "error": {
            "message": str(e),
            "type": type(e).__name__,
            "module": e.__class__.__module__,
            "line_number": e.__traceback__.tb_lineno if e.__traceback__ else None,
            "details": {
                "args": getattr(e, "args", None),
                "cause": str(e.__cause__) if e.__cause__ else None,
                "context": str(e.__context__) if e.__context__ else None,
            },
        },
    }
