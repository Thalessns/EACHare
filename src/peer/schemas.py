from dataclasses import dataclass


@dataclass
class Peer:
    address: str
    status: str = "OFFLINE"
