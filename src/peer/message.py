"""Modulo para mensagens de Peers"""
from dataclasses import dataclass


@dataclass
class MessageData:
    """Classe para representar uma mensagem
    
    Args:
        type (str): Tipo da mensagem
        content (str): Conteudo da mensagem
        warning (str): Mensagem de aviso para exibicao no console
    """
    type: str
    content: str
    warning: str


@dataclass
class ResponseMessage:
    """Classe para representar uma mensagem de resposta

    Args:
        warning (str): Mensagem de aviso para exibicao no console
    """
    warning: str


class Message:
    """Classe para representar mensagens enviadas e recebidas pelos peers"""

    @staticmethod
    def create(origin: str, clock: int, type: str, target: str, args: str = "") -> MessageData:
        """Cria uma mensagem para ser enviada
        
        Args:
            origin (str): Endereco do peer que envia a mensagem
            clock (int): Valor do relogio logico do peer que envia a mensagem
            type (str): Tipo da mensagem
            target (str): Endereco do peer que ira receber a mensagem
            args (str, optional): Argumentos adicionais da mensagem. Padrao eh vazio.
        """
        return MessageData(
            type=type,
            content=f"{origin} {clock} {type} {args}\n",
            warning=f"""Encaminhando mensagem "{origin} {clock} {type}" para {target}"""
        )

    @staticmethod
    def show_sent_warning(message: MessageData) -> None:
        """Exibe a mensagem de aviso no console.
        
        Args:
            message (MessageData): Mensagem enviada.
        """
        print(message.warning.replace("\n\n", ""))

    @staticmethod
    def show_receive_warning(message: str) -> None:
        """Exibe a mensagem recebida no console.
        
        Args:
            message (str): Mensagem recebida.
        """
        print(f"""\nMensagem recebida: "{message.replace("\n", "")}" """)

    @staticmethod
    def show_response_warning(message: str) -> None:
        """Exibe a mensagem de resposta recebida no console.
        
        Args:
            message (str): Mensagem de resposta recebida.
        """
        print(f"""Resposta recebida: "{message.replace("\n\n", "")}" """)

    @staticmethod
    def show_new_peer(new_peer: str, status: str) -> None:
        """Exibe a mensagem de novo peer no console.
        
        Args:
            new_peer (str): Endereco do novo peer.
            status (str): Status do novo peer.
        """
        print(f"Adicionando novo peer {new_peer} status {status}")

    @staticmethod
    def show_status_update(peer: str, status: str) -> None:
        """Exibe a mensagem de atualizacao de status no console.
        
        Args:
            peer (str): Endereco do peer.
            status (str): Novo status do peer.
        """
        print(f"Atualizando peer {peer} status {status}")

    @staticmethod
    def show_clock_update(clock: int) -> None:
        """Exibe a mensagem de atualizacao do relogio no console.
        
        Args:
            clock (int): Novo valor do relogio logico.
        """
        print(f"=> Atualizando relogio para {clock}")
