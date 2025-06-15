from dataclasses import dataclass


@dataclass
class StatData:
    chunk_size: int
    num_peers: int
    file_size: int
    time: float
