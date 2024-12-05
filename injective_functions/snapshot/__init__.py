import json
from typing import Dict, List
import requests

"""This class handles all the functions related to the snapshot module"""


class Snapshot():
    def __init__(self) -> None:
        # Initializes the network and the composer
        super().__init__()

    async def get_snapshot(self) -> List[Dict]:
        data = requests.get(
            "https://tokenstation.app/api/snapshots/last").json()

        return data
