from decimal import Decimal
from injective_functions.base import InjectiveBase
from injective_functions.utils.helpers import VaultContractType, SpotRedemptionType
from typing import List, Dict, Tuple
import json

# Set contract configuration based on network
CPMM_CONTRACT_CODE = 540
MITO_MASTER_CONTRACT_ADDRESS = "inj1vcqkkvqs7prqu70dpddfj7kqeqfdz5gg662qs3"


#TODO: Fetch vault details and abstract away the vault data through gpt
class InjectiveMitoContracts(InjectiveBase):
    def __init__(self, chain_client):
        super().__init__(chain_client)
        self.contract_type = {
            "ManagedVault": "crates.io:managed-vault",
            "CPMM": "crates.io:vault-cpmm-spot",
            "ASMMSpot": "crates.io:vault-cpmm-asmm-spot",
            "ASMMPerp": "crates.io:vault-cpmm-asmm-perp",
        }

    # TODO: add fetch functions to get mito launchpads
    # currently there is no python-sdk endpoints
    def _order_funds_by_denom(self, amounts: List[Tuple[float, str]]) -> str:
        """Sort and format funds by denom"""
        sorted_amounts = sorted(amounts, key=lambda x: x[1])
        return ",".join(f"{amount}{denom}" for amount, denom in sorted_amounts)

    # This section deals with all the transactions related to mito
    # Subscribe to Launchpad
    async def subscribe_to_launchpad(
        self, contract_address: str, quote_denom: str, amount: float
    ) -> Dict:
        json_data = json.dumps({"msg": {}, "action": "subscribe"})
        funds = f"{amount}{quote_denom}"
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=contract_address,
            msg=json_data,
            funds=funds,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    # Claim Launchpad Subscription
    async def claim_launchpad_subscription(self, contract_address: str) -> Dict:
        json_data = json.dumps({"msg": {}, "action": "Claim"})
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=contract_address,
            msg=json_data,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    # Subcribe to spot
    # TODO: Add support to derivative vaults
    async def subscription_mito_spot(
        self,
        base_amount: float,
        base_denom: str,
        quote_amount: float,
        quote_denom: str,
        vault_subaccount_id: str,
        max_penalty: float,
        vault_master_address: str,
        vault_contract_type: str,
        spot_redemption_type: str,
        trader_subaccount_idx: float = 0,
    ) -> Dict:
        """
        Subscribe to Mito spot trading vault
        """
        subscription_args = (
            {"slippage": {"max_penalty": str(max_penalty)}}
            if vault_contract_type == "CPMM"
            else {}
        )

        data = json.dumps({
            "vault_subaccount_id": vault_subaccount_id,
            "trader_subaccount_id": self.chain_client.address.get_subaccount_id(
                trader_subaccount_idx
            ),
            "msg": {"subscribe": subscription_args},
        })

        funds_list = []
        if spot_redemption_type != "QuoteOnly" and base_amount > 0:
            funds_list.append((base_amount, base_denom))
        if spot_redemption_type != "BaseOnly" and quote_amount > 0:
            funds_list.append((quote_amount, quote_denom))

        funds = self._order_funds_by_denom(funds_list)

        msg = self.chain_client.composer.msg_privileged_execute_contract(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=vault_master_address,
            msg=data,
            funds=funds,
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def redeem_mito_vault(
        self,
        redeem_amount: float,
        lp_denom: str,
        vault_subaccount_id: str,
        max_penalty: float,
        vault_master_address: str,
        market_type: str,
        redemption_type: str,
        trader_subaccount_idx: float = 0,
    ) -> Dict:
        """
        Redeem from Mito vault
        """
        subscription_args = (
            {"slippage": {"max_penalty": str(max_penalty)}}
            if market_type == "Derivative"
            else {}
        )
        subscription_args["redemption_type"] = redemption_type

        data = json.dumps({
            "vault_subaccount_id": vault_subaccount_id,
            "trader_subaccount_id": self.chain_client.address.get_subaccount_id(
                trader_subaccount_idx
            ),
            "msg": {"redeem": subscription_args},
        })

        funds = f"{redeem_amount}{lp_denom}"

        msg = self.chain_client.composer.msg_privileged_execute_contract(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=vault_master_address,
            msg=data,
            funds=funds,
        )

        return await self.chain_client.build_and_broadcast_tx(msg)

    async def stake_mito_vault(
        self,
        amount: float,
        vault_lp_denom: str,
        staking_contract_address: str,
    ) -> Dict:
        """
        Stake LP tokens in Mito vault
        """
        #TODO: verify if this has to be chain denom or not
        funds = f"{amount}{vault_lp_denom}"
        data = json.dumps({"action": "stake", "msg": {}})
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=staking_contract_address,
            msg=data,
            funds=funds,
        )

        return await self.chain_client.build_and_broadcast_tx(msg)
    
    async def unstake_mito(
        self,
        amount: float,
        vault_lp_denom: str,
        vault_token_decimals: int,
        staking_contract_address: str,
    ) -> Dict:
        """Unstake LP tokens from Mito vault"""
        amount_in_chain = int(amount * (10 ** vault_token_decimals))
        data = json.dumps({
                "action": "unstake",
                "msg": {
                    "coin": {
                        "denom": vault_lp_denom,
                        "amount": str(amount_in_chain)
                    }
                }
            })
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=staking_contract_address,
            msg=data
        )

        return await self.chain_client.build_and_broadcast_tx(msg)
    
    async def claim_stake_mito_vault(
        self,
        vault_lp_denom: str,
        staking_contract_address: str,
    ) -> Dict:
        """
        Claim staking rewards from Mito vault
        """
        data = json.dumps({
                "action": "claim_stake",
                "msg": {
                    "lp_token": vault_lp_denom
                }
            })
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=staking_contract_address,
            msg= data
        )

        return await self.chain_client.build_and_broadcast_tx(msg)
    async def claim_rewards_mito(
        self,
        vault_lp_denom: str,
        staking_contract_address: str,
    ) -> Dict:
        """
        Claim rewards from Mito vault
        """
        data  = json.dumps({
                "action": "claim_rewards",
                "msg": {
                    "lp_token": vault_lp_denom
                }
            })
        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=self.chain_client.address.to_acc_bech32(),
            contract=staking_contract_address,
            msg=data
        )

        return await self.chain_client.build_and_broadcast_tx(msg)
    
    #TODO: Need to test in testnet and improve parameterization of the default cpmm
    #This is the permissionless cpmm vault
    async def instantiate_cpmm_vault(
        self,
        base_token_amount: float,
        base_token_denom: str,
        quote_token_amount: float,
        quote_token_denom: str,
        market_id: str,
        fee_bps: int,
        base_decimals: int,
        quote_decimals: int,
        owner_address: str = None,
    ) -> Dict:
        """
        Instantiate a CPMM vault with specified parameters
        """
        if owner_address is None:
            owner_address = self.chain_client.address.to_acc_bech32()

        funds = [
            (quote_token_amount, quote_token_denom),
            (base_token_amount ,base_token_denom)
        ]
        funds = self._order_funds_by_denom(funds)
        data = {
            "action": "register_vault",
            "msg": {
                "is_subscribing_with_funds": True,
                "registration_mode": {
                    "permissionless": {
                        "whitelisted_vault_code_id": CPMM_CONTRACT_CODE
                    }
                },
                "instantiate_vault_msg": {
                    "Amm": {
                        "owner": owner_address,
                        "master_address": MITO_MASTER_CONTRACT_ADDRESS,
                        "notional_value_cap": "1000000000000000000000000",
                        "market_id": market_id,
                        "pricing_strategy": {
                            "SmoothingPricingWithRelativePriceRange": {
                                "bid_range": "0.8",
                                "ask_range": "0.8"
                            }
                        },
                        "max_invariant_sensitivity_bps": "5",
                        "max_price_sensitivity_bps": "5",
                        "fee_bps": fee_bps,
                        "order_type": "Vanilla",
                        "config_owner": owner_address,
                        "base_decimals": base_decimals,
                        "quote_decimals": quote_decimals
                    }
                }
            }
        }

        msg = self.chain_client.composer.msg_execute_contract_compat(
            sender=owner_address,
            contract=MITO_MASTER_CONTRACT_ADDRESS,
            msg=json.dumps(data),
            funds=funds,
        )

        return await self.chain_client.build_and_broadcast_tx(msg)