import statistics

from src.stats.schemas import StatData


class ManageStats:

    def __init__(self) -> None:
        self.data = []

    def save(
        self, 
        chunk_size: int,
        chunk_times: list[float],
        num_chunks: int,
        num_peers: int,
        file_size: int,
        total_time: int
    ) -> None:
        stat = StatData(
            chunk_size=chunk_size,
            chunk_times=chunk_times,
            num_chunks=num_chunks,
            num_peers=num_peers,
            file_size=file_size,
            deviation=statistics.stdev(chunk_times),
            total_time=total_time
        )
        self.data.append(stat)

    def get_data(self) -> list[StatData]:
        return self.data


manage_stats = ManageStats()