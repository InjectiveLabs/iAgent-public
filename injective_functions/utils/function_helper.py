# injective_functions/utils/function_mapping.py

from typing import Dict, Tuple, Any, Optional
import json
from pathlib import Path


class InjectiveFunctionMapper:
    # Map function names to (client_type, method_name)
    FUNCTION_MAP: Dict[str, Tuple[str, str]] = {
        # Trader functions
        "place_derivative_limit_order": ("trader", "place_derivative_limit_order"),
        "place_derivative_market_order": ("trader", "place_derivative_market_order"),
        "place_spot_limit_order": ("trader", "place_spot_limit_order"),
        "place_spot_market_order": ("trader", "place_spot_market_order"),
        "cancel_derivative_limit_order": ("trader", "cancel_derivative_limit_order"),
        "cancel_spot_limit_order": ("trader", "cancel_spot_limit_order"),
        # Exchange functions
        "get_subaccount_deposits": ("exchange", "get_subaccount_deposits"),
        "get_aggregate_market_volumes": ("exchange", "get_aggregate_market_volumes"),
        "get_aggregate_account_volumes": ("exchange", "get_aggregate_account_volumes"),
        "get_subaccount_orders": ("exchange", "get_subaccount_orders"),
        "get_historical_orders": ("exchange", "get_historical_orders"),
        "get_mid_price_and_tob_derivatives_market": (
            "exchange",
            "get_mid_price_and_tob_derivatives_market",
        ),
        "get_mid_price_and_tob_spot_market": (
            "exchange",
            "get_mid_price_and_tob_spot_market",
        ),
        "get_derivatives_orderbook": ("exchange", "get_derivatives_orderbook"),
        "get_spot_orderbook": ("exchange", "get_spot_orderbook"),
        "trader_derivative_orders": ("exchange", "trader_derivative_orders"),
        "trader_derivative_orders_by_hash": (
            "exchange",
            "trader_derivative_orders_by_hash",
        ),
        "trader_spot_orders": ("exchange", "trader_spot_orders"),
        "trader_spot_orders_by_hash": ("exchange", "trader_spot_orders_by_hash"),
        # Bank functions
        "query_balances": ("bank", "query_balances"),
        "transfer_funds": ("bank", "transfer_funds"),
        "query_spendable_balances": ("bank", "query_spendable_balances"),
        "query_total_supply": ("bank", "query_total_supply"),
        # Staking functions
        "stake_tokens": ("staking", "stake_tokens"),
        # Auction functions
        "send_bid_auction": ("auction", "send_bid_auction"),
        # Authz functions
        "grant_address_auth": ("authz", "grant_address_auth"),
        "revoke_address_auth": ("authz", "revoke_address_auth"),
        "fetch_grants": ("authz", "fetch_grants"),
        # Token factory functions
        "create_denom": ("token_factory", "create_denom"),
        "mint": ("token_factory", "mint"),
        "burn": ("token_factory", "burn"),
        "set_denom_metadata": ("token_factory", "set_denom_metadata"),

        "get_snapshot": ("snapshot", "get_snapshot"),
    }

    @classmethod
    def get_function_mapping(cls, function_name: str) -> Optional[Tuple[str, str]]:
        """Get the client type and method name for a given function"""
        return cls.FUNCTION_MAP.get(function_name)

    @classmethod
    def validate_function(cls, function_name: str) -> bool:
        """Check if a function name is valid"""
        return function_name in cls.FUNCTION_MAP

    @classmethod
    def get_all_client_types(cls) -> set:
        """Get all unique client types"""
        return {client_type for client_type, _ in cls.FUNCTION_MAP.values()}

    @classmethod
    def get_functions_for_client(cls, client_type: str) -> list:
        """Get all functions for a specific client type"""
        return [
            func_name
            for func_name, (client, _) in cls.FUNCTION_MAP.items()
            if client == client_type
        ]


class FunctionSchemaLoader:
    @staticmethod
    def load_schemas(schema_paths: list) -> dict:
        """Load and combine function schemas from multiple files"""
        combined_schemas = {"functions": []}

        for path in schema_paths:
            try:
                with open(path, "r") as f:
                    schema = json.load(f)
                    if "functions" in schema:
                        combined_schemas["functions"].extend(schema["functions"])
            except Exception as e:
                print(f"Error loading schema from {path}: {str(e)}")

        return combined_schemas["functions"]

    @staticmethod
    def validate_schema(schema: dict) -> bool:
        """Validate that a schema has the required structure"""
        if not isinstance(schema, dict):
            return False
        if "functions" not in schema:
            return False
        if not isinstance(schema["functions"], list):
            return False
        return True


class FunctionExecutor:
    @staticmethod
    async def execute_function(
        clients: Dict[str, Any], function_name: str, arguments: dict
    ) -> dict:
        """Execute a function with the appropriate client"""
        try:
            # Get the function mapping
            mapping = InjectiveFunctionMapper.get_function_mapping(function_name)
            if not mapping:
                return {"error": f"Function {function_name} not implemented"}

            client_type, method_name = mapping

            # Get the client
            client = clients.get(client_type)
            if not client:
                return {"error": f"Client type {client_type} not available"}

            # Get and execute the method
            method = getattr(client, method_name, None)
            if not method:
                return {
                    "error": f"Method {method_name} not found in {client_type} client"
                }

            return await method(**arguments)

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "details": {
                    "function": function_name,
                    "arguments": arguments,
                    "client_type": client_type if "client_type" in locals() else None,
                },
            }
