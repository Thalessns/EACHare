from src.stats.schemas import StatData


class ManageStats:

    def __init__(self) -> None:
        self.data = []

    def save(
        self, 
        chunk_size: int,
        num_peers: int,
        file_size: int,
        total_time: int
    ) -> None:
        stat = StatData(
            chunk_size=chunk_size,
            num_peers=num_peers,
            file_size=file_size,
            time=total_time
        )
        self.data.append(stat)

    def get_data(self) -> list[StatData]:
        return self.data


manage_stats = ManageStats()