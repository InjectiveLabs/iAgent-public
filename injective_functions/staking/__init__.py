import asyncio
from decimal import Decimal
from injective_functions.base import InjectiveBase
from typing import Dict


"""This class handles all account transfer within the account"""


class InjectiveStaking(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def stake_tokens(self, validator_address: str, amount: str) -> Dict:
        # prepare tx msg
        msg = self.chain_client.composer.MsgDelegate(
            delegator_address=self.chain_client.address.to_acc_bech32(),
            validator_address=validator_address,
            amount=float(amount),
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def compound_rewards(self, validator_address: str) -> Dict:
        """
        Compounds staking rewards by withdrawing them and restaking.
        :param validator_address: The validator's address
        :return: Transaction result
        """
        try:
            if not validator_address.startswith("injvaloper"):
                raise ValueError("Invalid validator address format")

            # Step 1: Fetch the initial INJ balance
            balance_response = await self.chain_client.client.get_bank_balance(
                address=self.chain_client.address.to_acc_bech32(),
                denom="inj"
            )
            initial_balance = Decimal(balance_response.balance.amount)

            # Step 2: Withdraw rewards
            withdraw_msg = self.chain_client.composer.msg_withdraw_delegator_reward(
                delegator_address=self.chain_client.address.to_acc_bech32(),
                validator_address=validator_address,
            )
            withdraw_response = await self.chain_client.build_and_broadcast_tx(withdraw_msg)

            # Step 3: Wait for the balance to update
            updated_balance = await self.wait_for_balance_update(old_balance=initial_balance, denom="inj")

            # Step 4: Calculate the withdrawn rewards
            rewards_to_stake = updated_balance - initial_balance
            if rewards_to_stake <= 0:
                if rewards_to_stake < 0:
                    # Specific error for negative rewards
                    return {
                        "success": False,
                        "error": f"Rewards ({rewards_to_stake}) are lower than gas fees, resulting in a negative net "
                                 f"reward."
                    }
                # Generic error for zero rewards
                return {"success": False, "error": "No rewards available to compound."}

            # Step 5: Restake the rewards
            delegate_msg = self.chain_client.composer.MsgDelegate(
                delegator_address=self.chain_client.address.to_acc_bech32(),
                validator_address=validator_address,
                amount=rewards_to_stake / Decimal('1e18'),
            )
            delegate_response = await self.chain_client.build_and_broadcast_tx(delegate_msg)

            return {
                "success": True,
                "withdraw_response": withdraw_response,
                "delegate_response": delegate_response,
            }

        except (TimeoutError, ValueError) as e:
            return {"success": False, "error": str(e)}

    async def wait_for_balance_update(
        self,
        old_balance: Decimal,
        denom: str,
        timeout: int = 10,
        interval: int = 1
    ) -> Decimal:
        """
        Waits for the balance to update after a transaction.
        :param old_balance: Previous balance to compare against
        :param denom: Denomination of the token (e.g., "inj")
        :param timeout: Total time to wait (in seconds)
        :param interval: Time between balance checks (in seconds)
        :return: Updated balance
        """
        if interval <= 0:
            raise ValueError("Interval must be greater than zero.")

        for _ in range(timeout // interval):
            balance_response = await self.chain_client.client.get_bank_balance(
                address=self.chain_client.address.to_acc_bech32(),
                denom=denom
            )
            updated_balance = Decimal(balance_response.balance.amount)
            if updated_balance != old_balance:
                return updated_balance
            await asyncio.sleep(interval)
        raise TimeoutError("Balance did not update within the timeout period.")
