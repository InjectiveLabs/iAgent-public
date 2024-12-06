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
        "fetch_auctions": ("auction", "fetch_auctions"),
        "fetch_latest_auction": ("auction", "fetch_latest_auction"),
        "fetch_auction_bids": ("auction", "fetch_auction_bids"),
        # Authz functions
        "grant_address_auth": ("authz", "grant_address_auth"),
        "revoke_address_auth": ("authz", "revoke_address_auth"),
        "fetch_grants": ("authz", "fetch_grants"),
        # Token factory functions
        "create_denom": ("token_factory", "create_denom"),
        "mint": ("token_factory", "mint"),
        "burn": ("token_factory", "burn"),
        "set_denom_metadata": ("token_factory", "set_denom_metadata"),
        # Mito fetch functions
        "get_vaults": ("mito_fetch_data", "get_vaults"),
        "get_vault": ("mito_fetch_data", "get_vault"),
        "get_lp_token_price_chart": ("mito_fetch_data", "get_lp_token_price_chart"),
        "get_tvl_chart": ("mito_fetch_data", "get_tvl_chart"),
        "get_vaults_by_holder_address": (
            "mito_fetch_data",
            "get_vaults_by_holder_address",
        ),
        "get_lp_holders": ("mito_fetch_data", "get_lp_holders"),
        "get_portfolio": ("mito_fetch_data", "get_portfolio"),
        "get_leaderboard": ("mito_fetch_data", "get_leaderboard"),
        "get_leaderboard_epochs": ("mito_fetch_data", "get_leaderboard_epochs"),
        "get_transfers_history": ("mito_fetch_data", "get_transfers_history"),
        "get_staking_pools": ("mito_fetch_data", "get_staking_pools"),
        "get_staking_reward_by_account": (
            "mito_fetch_data",
            "get_staking_reward_by_account",
        ),
        "get_staking_history": ("mito_fetch_data", "get_staking_history"),
        "get_staking_amount_at_height": (
            "mito_fetch_data",
            "get_staking_amount_at_height",
        ),
        "get_health": ("mito_fetch_data", "get_health"),
        "get_execution": ("mito_fetch_data", "get_execution"),
        "get_missions": ("mito_fetch_data", "get_missions"),
        "get_mission_leaderboard": ("mito,fetch_data", "get_mission_leaderboard"),
        "list_idos": ("mito_fetch_data", "list_idos"),
        "get_ido": ("mito_fetch_data", "get_ido"),
        "get_ido_subscribers": ("mito_fetch_data", "get_ido_subscribers"),
        "get_ido_subscription": ("mito_fetch_data", "get_ido_subscription"),
        "get_ido_activities": ("mito_fetch_data", "get_ido_activities"),
        "get_whitelist": ("mito_fetch_data", "get_whitelist"),
        "get_token_metadata": ("mito_fetch_data", "get_token_metadata"),
        "get_claim_references": ("mito_fetch_data", "get_claim_references"),
        # Mito txs
        "subscribe_to_launchpad": ("mito_transactions", "subscribe_to_launchpad"),
        "claim_launchpad_subscription": (
            "mito_transactions",
            "claim_launchpad_subscription",
        ),
        "subscription_mito_spot": ("mito_transactions", "subscription_mito_spot"),
        "redeem_mito_vault": ("mito_transactions", "redeem_mito_vault"),
        "stake_mito_vault": ("mito_transactions", "stake_mito_vault"),
        "unstake_mito": ("mito_transactions", "unstake_mito"),
        "claim_stake_mito_vault": ("mito_transactions", "claim_stake_mito_vault"),
        "claim_rewards_mito": ("mito_transactions", "claim_rewards_mito"),
        "instantiate_cpmm_vault": ("mito_transactions", "instantiate_cpmm_vault"),
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
