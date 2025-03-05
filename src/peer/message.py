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
            content=f"{origin} {clock} {type}{args}\n",
            warning=f"""Encaminhando mensagem "{origin} {clock} {type}" para {target}"""
        )
    
    @staticmethod
    def create_response(origin: str, clock: int, type: str, target: str, args: str = "") -> MessageData:
        return MessageData(
            content=f"{origin} {clock} {type} {args}\n",
            warning=f"""Encaminhando mensagem "{origin} {clock} {type}" para {target}"""
        )

