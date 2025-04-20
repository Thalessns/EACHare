from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class Peer:
    address: str
    status: str = "OFFLINE"
    clock: int = 0


@dataclass
class SharedFile:
    name: str
    bytes_size: int


@unique
class MessageType(Enum):

    HELLO = "HELLO"
    GET_PEERS = "GET_PEERS"
    LS = "LS"
    DL = "DL"
    BYE = "BYE"