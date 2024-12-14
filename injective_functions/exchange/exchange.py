from decimal import Decimal
from injective_functions.base import InjectiveBase
from injective_functions.utils.indexer_requests import fetch_decimal_denoms
from injective_functions.utils.helpers import (
    impute_market_id,
    impute_market_ids,
    detailed_exception_info,
)
from pyinjective.client.model.pagination import PaginationOption

from typing import Dict, List

class InjectiveExchange(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)
    
    async def get_subaccount_deposits(
        self, subaccount_idx: int, denoms: List[str] = None
    ) -> Dict:
        try:

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            deposits_response = (
                await self.chain_client.client.fetch_subaccount_deposits(
                    subaccount_id=subaccount_id
                )
            )
            deposits = deposits_response["deposits"]
            denom_decimals = await fetch_decimal_denoms(self.chain_client.network_type)
            human_readable_deposits = {}
            # checks if the denoms are specified
            if denoms:
                # iterate through the specified denoms
                for denom in denoms:
                    # Corner case 1: denom might not be in deposits found in chain data a case when gpt function calling parses wrong args
                    if denom in deposits and denom in denom_decimals:
                        human_readable_deposits[denom] = {
                            "available_balance": str(
                                int(deposits[denom]["availableBalance"])
                                / 10 ** int(denom_decimals[denom])
                            ),
                            "total_balance": str(
                                int(deposits[denom]["totalBalance"])
                                / 10 ** int(denom_decimals[denom])
                            ),
                        }
                    else:
                        human_readable_deposits[denom] = {
                            "available_balance": "balance not found",
                            "total_balance": "balance not found",
                        }
            # Otherwise we iterate through all the denoms
            else:
                for denom, deposit in deposits.items():
                    if denom in denom_decimals:
                        human_readable_deposits[denom] = {}
                        human_readable_deposits[denom]["available_balance"] = str(
                            int(deposit["availableBalance"])
                            / 10 ** denom_decimals[denom]
                        )

                        human_readable_deposits[denom]["total_balance"] = str(
                            int(deposit["totalBalance"]) / 10 ** denom_decimals[denom]
                        )
            return {"success": True, "result": human_readable_deposits}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_aggregate_market_volumes(self, market_ids=List[str]) -> Dict:
        try:
            market_ids = await impute_market_ids(market_ids)
            res = await self.chain_client.client.fetch_aggregate_market_volumes(
                market_ids=market_ids
            )
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_aggregate_account_volumes(
        self, market_ids: List[str], addresses: List[str]
    ) -> Dict:
        try:
            market_ids = await impute_market_ids(market_ids)
            res = await self.chain_client.client.fetch_aggregate_volumes(
                accounts=addresses,
                market_ids=market_ids,
            )
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_subaccount_orders(self, subaccount_idx: int, market_id: str) -> Dict:
        try:
            market_id = await impute_market_id(market_id)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            orders = await self.chain_client.client.fetch_chain_subaccount_orders(
                subaccount_id=subaccount_id,
                market_id=market_id,
            )
            return {"success": True, "result": orders}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_historical_orders(self, market_id: str) -> Dict:

        try:
            market_id = await impute_market_id(market_id)

            res = await self.chain_client.client.fetch_historical_trade_records(
                market_id=market_id
            )
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_mid_price_and_tob_derivatives_market(self, market_id: str) -> Dict:
        try:
            market_id = await impute_market_id(market_id)

            res = await self.chain_client.client.fetch_derivative_mid_price_and_tob(
                market_id=market_id,
            )
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_mid_price_and_tob_spot_market(self, market_id: str) -> Dict:
        try:
            market_id = await impute_market_id(market_id)

            res = await self.chain_client.client.fetch_spot_mid_price_and_tob(
                market_id=market_id,
            )
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_derivatives_orderbook(
        self, market_id: str, limit: int = None
    ) -> Dict:
        try:
            market_id = await impute_market_id(market_id)
            pagination = PaginationOption(limit)
            orderbook = await self.chain_client.client.fetch_chain_derivative_orderbook(
                market_id=market_id,
                pagination=pagination,
            )
            return {"success": True, "result": orderbook}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_spot_orderbook(self, market_id: str, limit: int = None) -> Dict:
        try:
            market_id = await impute_market_id(market_id)
            pagination = PaginationOption(limit)
            orderbook = await self.chain_client.client.fetch_chain_spot_orderbook(
                market_id=market_id,
                pagination=pagination,
            )
            return {"success": True, "result": orderbook}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def trader_derivative_orders(self, market_id: str, subaccount_idx: int):
        try:

            market_id = await impute_market_id(market_id)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            orders = (
                await self.chain_client.client.fetch_chain_trader_derivative_orders(
                    market_id=market_id,
                    subaccount_id=subaccount_id,
                )
            )
            return {"success": True, "result": orders}
        except Exception as e:
            return {"success": False, "result": detailed_exception_info(e)}

    async def trader_spot_orders(self, market_id: str, subaccount_idx: int):
        try:
            market_id = await impute_market_id(market_id)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            orders = await self.chain_client.client.fetch_chain_trader_spot_orders(
                market_id=market_id,
                subaccount_id=subaccount_id,
            )
            return {"success": True, "result": orders}
        except Exception as e:
            return {"success": False, "result": detailed_exception_info(e)}

    async def trader_derivative_orders_by_hash(
        self, market_id: str, subaccount_idx: int, order_hashes: List[str]
    ) -> Dict:
        try:
            market_id = await impute_market_id(market_id)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            orders = (
                await self.chain_client.client.fetch_chain_derivative_orders_by_hashes(
                    market_id=market_id,
                    subaccount_id=subaccount_id,
                    order_hashes=order_hashes,
                )
            )
            return {"success": True, "result": orders}
        except Exception as e:
            return {"success": False, "result": detailed_exception_info(e)}

    async def trader_spot_orders_by_hash(
        self, market_id: str, subaccount_idx: int, order_hashes: List[str]
    ) -> Dict:
        try:
            market_id = await impute_market_id(market_id)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
            orders = await self.chain_client.client.fetch_chain_spot_orders_by_hashes(
                market_id=market_id,
                subaccount_id=subaccount_id,
                order_hashes=order_hashes,
            )
            return {"success": True, "result": orders}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def get_subaccount_positions_in_markets(self, market_ids: List[str]) -> Dict:
        try:
            market_ids = await impute_market_ids(market_ids)

            subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_id)
            positions = await self.chain_client.client.fetch_chain_subaccount_positions(
                subaccount_id=subaccount_id,
            )["state"]
            position_map = {}
            for position in positions:
                position_map[position["market_id"]] = position["position"]

            filtered_positions = dict()
            if market_ids != None:
                for market_id in market_ids:
                    filtered_positions["market_id"] = position_map[market_id]
                return {"success": True, "result": position_map}
            return {"success": True, "result": position_map}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def launch_instant_spot_market(
        self,
        ticker: str,
        base: str,
        quote: str,
        min_price_tick: str,
        min_quantity_tick: str,
        min_notional: str,
    ) -> Dict:
        try:
            await self.chain_client.init_client()
            msg = self.chain_client.composer.msg_instant_spot_market_launch(
                sender=self.chain_client.address.to_acc_bech32(),
                ticker=ticker,
                base_denom=base,
                quote_denom=quote,
                min_price_tick_size=Decimal(min_price_tick),
                min_quantity_tick_size=Decimal(min_quantity_tick),
                min_notional=Decimal(min_notional),
            )
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def launch_instant_perp_market(
        self,
        ticker: str,
        quote_denom: str,
        oracle_base: str,
        oracle_quote: str,
        oracle_scale_factor: int,
        oracle_type: str,
        maker_fee_rate: str,
        taker_fee_rate: str,
        initial_margin_ratio: str,
        maintenance_margin_ratio: str,
        min_price_tick: str,
        min_quantity_tick: str,
        min_notional_size: str,
    ) -> Dict:
        try:

            await self.chain_client.init_client()
            msg = self.chain_client.composer.msg_instant_perpetual_market_launch(
                sender=self.chain_client.address.to_acc_bech32(),
                ticker=ticker,
                quote_denom=quote_denom,
                oracle_base=oracle_base,
                oracle_quote=oracle_quote,
                oracle_scale_factor=oracle_scale_factor,
                oracle_type=oracle_type,
                maker_fee_rate=Decimal(maker_fee_rate),
                taker_fee_rate=Decimal(taker_fee_rate),
                initial_margin_ratio=Decimal(initial_margin_ratio),
                maintenance_margin_ratio=Decimal(maintenance_margin_ratio),
                min_price_tick_size=Decimal(min_price_tick),
                min_quantity_tick_size=Decimal(min_quantity_tick),
                min_notional=Decimal(min_notional_size),
            )
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def opt_out_trade_earn_rewards(self) -> Dict:

        msg = self.chain_client.composer.msg_rewards_opt_out(
            sender=self.chain_client.address.to_acc_bech32()
        )
        await self.chain_client.build_and_broadcast_tx(msg)
