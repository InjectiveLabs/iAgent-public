from typing import Dict
from injective_functions.base import InjectiveBase
from injective_functions.utils.helpers import detailed_exception_info

# TODO: Convert raw exchange message formats to human readable


class InjectiveTokenFactory(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def create_denom(
        self, subdenom: str, name: str, symbol: str, decimals: int
    ) -> Dict:
        try:
            await self.chain_client.init_client()
            msg = self.chain_client.composer.msg_create_denom(
                sender=self.chain_client.address.to_acc_bech32(),
                subdenom=subdenom,
                name=name,
                symbol=symbol,
                decimals=decimals,
            )

            # broadcast the transaction
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def mint(self, denom: str, amount: int) -> Dict:
        try:
            await self.chain_client.init_client()
            amount = self.chain_client.composer.coin(amount=amount, denom=denom)
            msg = self.chain_client.composer.msg_mint(
                sender=self.chain_client.address.to_acc_bech32(),
                amount=amount,
            )

            # broadcast the transaction
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def burn(self, denom: str, amount: int) -> Dict:
        try:
            await self.chain_client.init_client()
            amount = self.chain_client.composer.coin(amount=amount, denom=denom)
            msg = self.chain_client.composer.msg_burn(
                sender=self.chain_client.address.to_acc_bech32(),
                amount=amount,
            )

            # broadcast the transaction
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}

    async def set_denom_metadata(
        self,
        sender: str,
        description: str,
        denom: str,
        subdenom: str,
        token_decimals: int,
        name: str,
        symbol: str,
        uri: str,
        uri_hash: str,
    ) -> Dict:
        try:

            msg = self.chain_client.composer.msg_set_denom_metadata(
                sender=sender,
                description=description,
                denom=denom,
                subdenom=subdenom,
                token_decimals=token_decimals,
                name=name,
                symbol=symbol,
                uri=uri,
                uri_hash=uri_hash,
            )

            # broadcast the transaction
            res = await self.chain_client.message_broadcaster.broadcast([msg])
            return {"success": True, "result": res}
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
