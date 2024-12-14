import uuid
from decimal import Decimal
from injective_functions.base import InjectiveBase
from injective_functions.utils.helpers import impute_market_id, base64convert

# TODO: serve endpoints of trader functions via an api
# to isolate functions as much as possible
# app = Flask(__name__)


class InjectiveTrading(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def place_derivative_limit_order(
        self,
        price: float,
        quantity: float,
        side: str,
        market_id: str,
        subaccount_idx: int,
        leverage: str,
    ):
        """Place a limit order"""
        market_id = await impute_market_id(market_id)
        self.subaccount_id = self.chain_client.address.get_subaccount_id(
            index=subaccount_idx
        )
        msg = self.chain_client.composer.msg_create_derivative_limit_order(
            sender=self.chain_client.address.to_acc_bech32(),
            fee_recipient=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=self.subaccount_id,
            price=Decimal(str(price)),
            quantity=Decimal(str(quantity)),
            margin=self.chain_client.composer.calculate_margin(
                quantity=Decimal(str(quantity)),
                price=Decimal(str(price)),
                leverage=Decimal(leverage),
                is_reduce_only=False,
            ),
            order_type=side,
            cid=str(uuid.uuid4()),
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def place_derivative_market_order(
        self,
        quantity: float,
        side: str,
        market_id: str,
        subaccount_idx: int,
        leverage: str,
    ):
        """Place a market order"""

        market_id = await impute_market_id(market_id)
        self.subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
        # For market orders, we'll use the current price as an estimate
        # this gets bbo and mid from composer.
        estimated_price = (
            await self.chain_client.client.fetch_derivative_mid_price_and_tob(
                market_id=market_id
            )["midPrice"]
        )

        msg = self.chain_client.composer.msg_create_derivative_market_order(
            sender=self.chain_client.address.to_acc_bech32(),
            fee_recipient=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=self.subaccount_id,
            price=Decimal(estimated_price),
            quantity=Decimal(str(quantity)),
            margin=self.chain_client.composer.calculate_margin(
                quantity=Decimal(str(quantity)),
                price=Decimal(estimated_price),
                leverage=Decimal(leverage),
                is_reduce_only=False,
            ),
            order_type=side,
            cid=str(uuid.uuid4()),
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def cancel_derivative_limit_order(
        self, market_id: str, subaccount_idx: int, order_hash: str
    ):
        market_id = await impute_market_id(market_id)
        converted_order_hash = base64convert(order_hash)
        subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
        msg = self.chain_client.composer.msg_cancel_derivative_order(
            sender=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=subaccount_id,
            order_hash=converted_order_hash,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def place_spot_limit_order(
        self,
        price: float,
        quantity: float,
        side: str,
        market_id: str,
        subaccount_idx: int,
    ):
        """Place a limit order"""

        market_id = await impute_market_id(market_id)
        self.subaccount_id = self.chain_client.address.get_subaccount_id(
            index=subaccount_idx
        )
        msg = self.chain_client.composer.msg_create_spot_limit_order(
            sender=self.chain_client.address.to_acc_bech32(),
            fee_recipient=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=self.subaccount_id,
            price=Decimal(str(price)),
            quantity=Decimal(str(quantity)),
            order_type=side,
            cid=str(uuid.uuid4()),
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def place_spot_market_order(
        self, quantity: float, side: str, market_id: str, subaccount_idx: int
    ):
        """Place a market order"""

        market_id = await impute_market_id(market_id)
        self.subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
        # For market orders, we'll use the current price as an estimate
        # this gets bbo and mid from composer.
        estimated_price = (
            await self.chain_client.client.fetch_derivative_mid_price_and_tob(
                market_id=market_id
            )["midPrice"]
        )

        msg = self.chain_client.composer.msg_create_spot_market_order(
            sender=self.chain_client.address.to_acc_bech32(),
            fee_recipient=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=self.subaccount_id,
            price=Decimal(estimated_price),
            quantity=Decimal(str(quantity)),
            order_type=side,
            cid=str(uuid.uuid4()),
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def cancel_spot_limit_order(
        self, market_id: str, subaccount_idx: int, order_hash: str
    ):
        converted_order_hash = base64convert(order_hash)
        market_id = await impute_market_id(market_id)
        subaccount_id = self.chain_client.address.get_subaccount_id(subaccount_idx)
        msg = self.chain_client.composer.msg_cancel_spot_order(
            sender=self.chain_client.address.to_acc_bech32(),
            market_id=market_id,
            subaccount_id=subaccount_id,
            order_hash=converted_order_hash,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)
