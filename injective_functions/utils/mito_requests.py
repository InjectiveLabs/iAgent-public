import aiohttp


class MitoAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def _request(self, method: str, path: str, **query_params):
        # Remove any query_params that are None
        query_params = {k: v for k, v in query_params.items() if v is not None}

        url = f"{self.base_url}{path}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, params=query_params) as response:
                response.raise_for_status()
                return await response.json()

    # Endpoint: GetVaults
    # Path: /vaults
    # Query params: limit, pageIndex, codeID
    async def get_vaults(
        self, limit: int = None, pageIndex: int = None, codeID: str = None
    ):
        return await self._request(
            "GET", "/vaults", limit=limit, pageIndex=pageIndex, codeID=codeID
        )

    # Endpoint: GetVault
    # Path: /vault
    # Query params: slug, contractAddress
    async def get_vault(self, slug: str = None, contractAddress: str = None):
        return await self._request(
            "GET", "/vault", slug=slug, contractAddress=contractAddress
        )

    # Endpoint: LPTokenPriceChart
    # Path: /vaults/{vaultAddress}/lpTokenPriceChart
    # Path param: vaultAddress
    # Query params: fromTime, toTime
    async def get_lp_token_price_chart(
        self, vaultAddress: str, fromTime: str = None, toTime: str = None
    ):
        path = f"/vaults/{vaultAddress}/lpTokenPriceChart"
        return await self._request("GET", path, fromTime=fromTime, toTime=toTime)

    # Endpoint: TVLChart
    # Path: /vaults/{vaultAddress}/tvlChart
    # Path param: vaultAddress
    # Query params: fromTime, toTime
    async def get_tvl_chart(
        self, vaultAddress: str, fromTime: str = None, toTime: str = None
    ):
        path = f"/vaults/{vaultAddress}/tvlChart"
        return await self._request("GET", path, fromTime=fromTime, toTime=toTime)

    # Endpoint: VaultsByHolderAddress
    # Path: /holders/{holderAddress}/vaults
    # Path param: holderAddress
    # Query params: limit, pageIndex, vaultAddress, skip
    async def get_vaults_by_holder_address(
        self,
        holderAddress: str,
        limit: int = None,
        pageIndex: int = None,
        vaultAddress: str = None,
        skip: int = None,
    ):
        path = f"/holders/{holderAddress}/vaults"
        return await self._request(
            "GET",
            path,
            limit=limit,
            pageIndex=pageIndex,
            vaultAddress=vaultAddress,
            skip=skip,
        )

    # Endpoint: LPHolders
    # Path: /vaults/{vaultAddress}/holders
    # Path param: vaultAddress
    # Query params: limit, pageIndex, stakingContractAddress, skip
    async def get_lp_holders(
        self,
        vaultAddress: str,
        limit: int = None,
        pageIndex: int = None,
        stakingContractAddress: str = None,
        skip: int = None,
    ):
        path = f"/vaults/{vaultAddress}/holders"
        return await self._request(
            "GET",
            path,
            limit=limit,
            pageIndex=pageIndex,
            stakingContractAddress=stakingContractAddress,
            skip=skip,
        )

    # Endpoint: Portfolio
    # Path: /holders/{holderAddress}/portfolio
    # Path param: holderAddress
    # Query params: stakingContractAddress
    async def get_portfolio(
        self, holderAddress: str, stakingContractAddress: str = None
    ):
        path = f"/holders/{holderAddress}/portfolio"
        return await self._request(
            "GET", path, stakingContractAddress=stakingContractAddress
        )

    # Endpoint: Leaderboard
    # Path: /leaderboard
    async def get_leaderboard(self):
        return await self._request("GET", "/leaderboard")

    # Endpoint: LeaderboardEpochs
    # Path: /leaderboards
    # Query params: fromEpochId, toEpochId, limit
    async def get_leaderboard_epochs(
        self, fromEpochId: int = None, toEpochId: int = None, limit: int = None
    ):
        return await self._request(
            "GET",
            "/leaderboards",
            fromEpochId=fromEpochId,
            toEpochId=toEpochId,
            limit=limit,
        )

    # Endpoint: TransfersHistory
    # Path: /transfersHistory
    # Query params: vault, account, limit, fromNumber, toNumber
    async def get_transfers_history(
        self,
        vault: str = None,
        account: str = None,
        limit: int = None,
        fromNumber: int = None,
        toNumber: int = None,
    ):
        return await self._request(
            "GET",
            "/transfersHistory",
            vault=vault,
            account=account,
            limit=limit,
            fromNumber=fromNumber,
            toNumber=toNumber,
        )

    # Endpoint: GetStakingPools
    # Path: /stakingPools
    # Query params: staker, stakingContractAddress
    async def get_staking_pools(
        self, staker: str = None, stakingContractAddress: str = None
    ):
        return await self._request(
            "GET",
            "/stakingPools",
            staker=staker,
            stakingContractAddress=stakingContractAddress,
        )

    # Endpoint: StakingRewardByAccount
    # Path: /holders/{staker}/stakingRewards
    # Path param: staker
    # Query params: stakingContractAddress
    async def get_staking_reward_by_account(
        self, staker: str, stakingContractAddress: str = None
    ):
        path = f"/holders/{staker}/stakingRewards"
        return await self._request(
            "GET", path, stakingContractAddress=stakingContractAddress
        )

    # Endpoint: StakingHistory
    # Path: /stakingHistory
    # Query params: fromNumber, toNumber, limit, staker
    async def get_staking_history(
        self,
        fromNumber: int = None,
        toNumber: int = None,
        limit: int = None,
        staker: str = None,
    ):
        return await self._request(
            "GET",
            "/stakingHistory",
            fromNumber=fromNumber,
            toNumber=toNumber,
            limit=limit,
            staker=staker,
        )

    # Endpoint: StakingAmountAtHeight
    # Path: /stakingHistory/{stakingContractAddress}/amounts
    # Path param: stakingContractAddress
    # Query params: denom, height, staker, skip, limit
    async def get_staking_amount_at_height(
        self,
        stakingContractAddress: str,
        denom: str = None,
        height: str = None,
        staker: str = None,
        skip: int = None,
        limit: int = None,
    ):
        path = f"/stakingHistory/{stakingContractAddress}/amounts"
        return await self._request(
            "GET",
            path,
            denom=denom,
            height=height,
            staker=staker,
            skip=skip,
            limit=limit,
        )

    # Endpoint: Health
    # Path: /health
    async def get_health(self):
        return await self._request("GET", "/health")

    # Endpoint: Execution
    # Path: /execution/{contractAddress}
    # Path param: contractAddress
    async def get_execution(self, contractAddress: str):
        path = f"/execution/{contractAddress}"
        return await self._request("GET", path)

    # Endpoint: Missions
    # Path: /missions/{account_address}
    # Path param: account_address
    async def get_missions(self, account_address: str):
        path = f"/missions/{account_address}"
        return await self._request("GET", path)

    # Endpoint: MissionLeaderboard
    # Path: /missionsLeaderboard
    # Query params: userAddress
    async def get_mission_leaderboard(self, userAddress: str = None):
        return await self._request(
            "GET", "/missionsLeaderboard", userAddress=userAddress
        )

    # Endpoint: ListIDOs
    # Path: /launchpad/idos
    # Query params: status, limit, toNumber, accountAddress, ownerAddress
    async def list_idos(
        self,
        status: str = None,
        limit: int = None,
        toNumber: int = None,
        accountAddress: str = None,
        ownerAddress: str = None,
    ):
        return await self._request(
            "GET",
            "/launchpad/idos",
            status=status,
            limit=limit,
            toNumber=toNumber,
            accountAddress=accountAddress,
            ownerAddress=ownerAddress,
        )

    # Endpoint: GetIDO
    # Path: /launchpad/idos/{contractAddress}
    # Path param: contractAddress
    # Query params: accountAddress
    async def get_ido(self, contractAddress: str, accountAddress: str = None):
        path = f"/launchpad/idos/{contractAddress}"
        return await self._request("GET", path, accountAddress=accountAddress)

    # Endpoint: GetIDOSubscribers
    # Path: /launchpad/idos/{contractAddress}/subscribers
    # Path param: contractAddress
    # Query params: limit, skip, sortBy
    async def get_ido_subscribers(
        self,
        contractAddress: str,
        limit: int = None,
        skip: int = None,
        sortBy: str = None,
    ):
        path = f"/launchpad/idos/{contractAddress}/subscribers"
        return await self._request("GET", path, limit=limit, skip=skip, sortBy=sortBy)

    # Endpoint: GetIDOSubscription
    # Path: /launchpad/idos/{contractAddress}/subscription/{accountAddress}
    # Path params: contractAddress, accountAddress
    async def get_ido_subscription(self, contractAddress: str, accountAddress: str):
        path = f"/launchpad/idos/{contractAddress}/subscription/{accountAddress}"
        return await self._request("GET", path)

    # Endpoint: GetIDOActivities
    # Path: /launchpad/activities
    # Query params: contractAddress, accountAddress, limit, toNumber
    async def get_ido_activities(
        self,
        contractAddress: str = None,
        accountAddress: str = None,
        limit: int = None,
        toNumber: int = None,
    ):
        return await self._request(
            "GET",
            "/launchpad/activities",
            contractAddress=contractAddress,
            accountAddress=accountAddress,
            limit=limit,
            toNumber=toNumber,
        )

    # Endpoint: GetWhitelist
    # Path: /launchpad/idos/{idoAddress}/whitelist
    # Path param: idoAddress
    # Query params: skip, limit
    async def get_whitelist(self, idoAddress: str, skip: int = None, limit: int = None):
        path = f"/launchpad/idos/{idoAddress}/whitelist"
        return await self._request("GET", path, skip=skip, limit=limit)

    # Endpoint: TokenMetadata
    # Path: /tokenMetadata
    async def get_token_metadata(self):
        return await self._request("GET", "/tokenMetadata")

    # Endpoint: GetClaimReferences
    # Path: /launchpad/claimReferences/
    # Query params: accountAddress, idoAddress, skip, limit
    async def get_claim_references(
        self, accountAddress: str, idoAddress: str, skip: int = None, limit: int = None
    ):
        return await self._request(
            "GET",
            "/launchpad/claimReferences/",
            accountAddress=accountAddress,
            idoAddress=idoAddress,
            skip=skip,
            limit=limit,
        )


# import asyncio
#
# async def main():
#     client = MitoAPIClient("https://k8s.mainnet.mito.grpc-web.injective.network/api/v1")
#     vaults = await client.get_vaults(limit=5)
#     print(vaults)
#
# asyncio.run(main())
