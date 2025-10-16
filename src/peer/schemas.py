"""Schemas de dados usados no peer-to-peer."""

from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class Peer:
    """Classe para representar um peer na rede P2P.
    
    Args:
        address (str): Endereco do peer.
        status (str, optional): Status do peer. Padrao eh "OFFLINE".
        clock (int, optional): Valor do relogio logico do peer. Padrao eh 0.
    """
    address: str
    status: str = "OFFLINE"
    clock: int = 0


@dataclass
class SharedFile:
    """Classe para representar um arquivo compartilhado na rede P2P.
    
    Args:
        name (str): Nome do arquivo.
        bytes_size (int): Tamanho do arquivo em bytes.
    """
    name: str
    bytes_size: int


@unique
class MessageType(Enum):
    """Enum para representar os tipos de mensagens na rede P2P.
    
    Args:
        Hello (str): Mensagem de saudacao.
        GetPeers (str): Mensagem para requisitar a lista de peers.
        Ls (str): Mensagem para listar arquivos compartilhados.
        Dl (str): Mensagem para requisitar o download de um arquivo.
        Bye (str): Mensagem de despedida.
    """
    HELLO = "HELLO"
    GET_PEERS = "GET_PEERS"
    LS = "LS"
    DL = "DL"
    BYE = "BYE"
