from decimal import Decimal
from injective_functions.base import InjectiveBase
from injective_functions.utils.helpers import get_bridge_fee, detailed_exception_info
from typing import Dict


"""This class handles all account transfer within the account"""


class InjectiveAccounts(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    # We're using the MsgSubaccountTransfer
    # Handle errors properly here
    async def subaccount_transfer(
        self, amount: str, denom: str, subaccount_idx: int, dst_subaccount_idx: int
    ) -> Dict:

        source_subaccount_id = self.chain_client.address.get_subaccount_id(
            subaccount_idx
        )
        dst_subaccount_id = self.chain_client.address.get_subaccount_id(
            dst_subaccount_idx
        )
        msg = self.chain_client.composer.msg_subaccount_transfer(
            sender=self.chain_client.address.to_acc_bech32(),
            source_subaccount_id=source_subaccount_id,
            destination_subaccount_id=dst_subaccount_id,
            amount=Decimal(amount),
            denom=denom,
        )
        await self.chain_client.build_and_broadcast_tx(msg)

    # External subaccount transfer
    async def external_subaccount_transfer(
        self, amount: str, denom: str, subaccount_idx: int, dst_subaccount_id: str
    ) -> Dict:

        source_subaccount_id = self.chain_client.address.get_subaccount_id(
            subaccount_idx
        )
        msg = self.chain_client.composer.msg_external_transfer(
            sender=self.chain_client.address.to_acc_bech32(),
            source_subaccount_id=source_subaccount_id,
            destination_subaccount_id=dst_subaccount_id,
            amount=Decimal(amount),
            denom=denom,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def send_to_eth(self, denom: str, eth_dest: str, amount: str):

        bridge_fee = get_bridge_fee()
        # prepare tx msg
        msg = self.chain_client.composer.MsgSendToEth(
            sender=self.chain_client.address.to_acc_bech32(),
            denom=denom,
            eth_dest=eth_dest,
            amount=Decimal(amount),
            bridge_fee=bridge_fee,
        )
        await self.chain_client.build_and_broadcast_tx(msg)

    async def fetch_tx(self, tx_hash: str) -> Dict:
        try:
            res = await self.chain_client.client.fetch_tx(hash=tx_hash)
            return {
                "success": True,
                "result": res,
            }
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
