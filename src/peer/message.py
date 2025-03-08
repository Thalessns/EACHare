from dataclasses import dataclass


@dataclass
class MessageData:
    content: str
    warning: str


@dataclass
class ResponseMessage:
    warning: str


class Message:

    @staticmethod
    def create(origin: str, clock: int, type: str, target: str, args: str = "") -> MessageData:
        return MessageData(
            content=f"{origin} {clock} {type} {args}\n",
            warning=f"""Encaminhando mensagem "{origin} {clock} {type}" para {target}"""
        )

    @staticmethod
    def show_sent_warning(message: MessageData) -> None:
        print(message.warning.replace("\n\n", ""))

    @staticmethod
    def show_receive_warning(message: str) -> None:
        print(f"""\nMensagem recebida: "{message.replace("\n", "")}" """)

    @staticmethod
    def show_response_warning(message: str) -> None:
        print(f"""Resposta recebida: "{message.replace("\n\n", "")}" """)

    @staticmethod
    def show_new_peer(new_peer: str, status: str) -> None:
        print(f"Adicionando novo peer {new_peer} status {status}")

    @staticmethod
    def show_status_update(peer: str, status: str) -> None:
        print(f"Atualizando peer {peer} status {status}")

    @staticmethod
    def show_clock_update(clock: int) -> None:
        print(f"=> Atualizando relogio para {clock}")