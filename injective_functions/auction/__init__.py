from decimal import Decimal
from injective_functions.base import InjectiveBase
from typing import Dict
from injective_functions.utils.helpers import (
    detailed_exception_info,
)


"""This class handles all auction messages"""


# TODO: add fetch current round function on indexer helper
class InjectiveAuction(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def send_bid_auction(self, round: int, amount: str) -> Dict:
        await self.chain_client.init_client()
        msg = self.chain_client.composer.MsgBid(
            sender=self.chain_client.address.to_acc_bech32(),
            round=round,
            bid_amount=Decimal(amount),
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def fetch_auctions(self) -> Dict:
        try:
            auctions = await self.chain_client.client.fetch_auctions()
            return {"success": True, "result": auctions["auctions"]}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def fetch_latest_auction(self) -> Dict:
        try:
            result = await self.fetch_auctions()
            if result["success"]:
                return {"success": True, "result": result["result"][-1]}
            else:
                return {"success": False, "error": "failed to fetch auction data"}

        except Exception as e:
            return {"success": False, "result": detailed_exception_info(e)}

    async def fetch_auction_bids(self, bid_round: int) -> Dict:
        try:
            auction = await self.chain_client.client.fetch_auction(round=bid_round)
            return {"success": True, "result": auction["bids"]}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
