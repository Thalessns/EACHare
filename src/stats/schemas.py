from dataclasses import dataclass


@dataclass
class StatData:
    chunk_size: int
    chunk_times: list[float]
    num_chunks: int
    num_peers: int
    file_size: int
    deviation: float
    total_time: float
