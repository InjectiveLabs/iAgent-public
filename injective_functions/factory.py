from typing import Dict
from injective_functions.utils.initializers import ChainInteractor
from injective_functions.account import InjectiveAccounts
from injective_functions.auction import InjectiveAuction
from injective_functions.authz import InjectiveAuthz
from injective_functions.bank import InjectiveBank
from injective_functions.exchange.exchange import InjectiveExchange
from injective_functions.exchange.trader import InjectiveTrading
from injective_functions.staking import InjectiveStaking
from injective_functions.token_factory import InjectiveTokenFactory
from injective_functions.utils.mito_requests import MitoAPIClient
from injective_functions.wasm.mito_contracts import InjectiveMitoContracts

MITO_BASE_URI = "https://k8s.mainnet.mito.grpc-web.injective.network/api/v1"
class InjectiveClientFactory:
    """Factory for creating Injective client instances."""

    @staticmethod
    async def create_all(private_key: str, network_type: str = "mainnet") -> Dict:
        """
        Create instances of all Injective modules sharing one ChainInteractor.

        Args:
            private_key (str): Private key for blockchain interactions
            network_type (str, optional): Network type. Defaults to "mainnet".

        Returns:
            Dict: Dictionary containing all initialized clients
        """
        # Create and initialize the chain client
        chain_client = ChainInteractor(
            network_type=network_type, private_key=private_key
        )
        await chain_client.init_client()  # This line is crucial!

        # Create instances with the initialized chain client
        clients = {
            "account": InjectiveAccounts(chain_client),
            "auction": InjectiveAuction(chain_client),
            "authz": InjectiveAuthz(chain_client),
            "bank": InjectiveBank(chain_client),
            "exchange": InjectiveExchange(chain_client),
            "trader": InjectiveTrading(chain_client),
            "staking": InjectiveStaking(chain_client),
            "token_factory": InjectiveTokenFactory(chain_client),
            "mito_fetch_data": MitoAPIClient(MITO_BASE_URI),
            "mito_transactions": InjectiveMitoContracts(chain_client)
        }
        print(clients)
        return clients
