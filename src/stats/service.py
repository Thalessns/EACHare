"""Modulo para lidar com as estatisticas do Peer."""
import statistics

from src.stats.schemas import StatData


class ManageStats:
    """Classe para gerenciar as estatisticas do Peer."""
    def __init__(self) -> None:
        """Inicializa a classe."""
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
        """Salva as estatisticas do Peer.

        Args:
            chunk_size (int): Tamanho do chunk.
            chunk_times (list[float]): Tempos de download dos chunks.
            num_chunks (int): Numero de chunks.
            num_peers (int): Numero de peers.
            file_size (int): Tamanho do arquivo.
            total_time (int): Tempo total de download.
        """
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
        """Retorna as estatisticas do Peer.

        Returns:
            list[StatData]: Lista de estatisticas do Peer.
        """
        return self.data


manage_stats = ManageStats()
