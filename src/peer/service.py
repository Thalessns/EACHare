import socket
import threading

from typing import List, Union

from src.peer.message import MessageData, Message
from src.peer.schemas import Peer


class PeerService:

    def __init__(self, address: str, peers_file_path: str, shared_directory: str) -> None:
        self.status = {
        True: "ONLINE",
        False: "OFFLINE"
        }
        self.handle_type = {
            "HELLO": self._handle_hello,
            "GET_PEERS": self._handle_get_peers,
            "BYE": self._handle_bye
        }
        self.clock = 0
        self.address = address
        self.peers_file_path = peers_file_path
        self.shared_directory = shared_directory
        self.known_peers = self.read_known_peers()

    def read_known_peers(self) -> List[Peer]:
        known_peers = []
        with open(self.peers_file_path, "r") as file:
            peers = file.readlines()
            for peer in peers:
                address = peer.replace("\n", "")
                if address == self.address: 
                    continue
                known_peers.append(Peer(address=address))
            file.close()
        return known_peers
    
    def insert_known_peer(self, new_peer: str, status: bool = True) -> None:
        if new_peer == self.address:
            return
        target = self.get_peer(new_peer) 
        if not target:
            print(f"Adicionando novo peer {new_peer} status {self.status.get(status)}")
            with open(self.peers_file_path, "a") as file:
                file.write(new_peer+"\n")
                file.close()
            target = Peer(address=new_peer)
            self.known_peers.append(target)
        target.status = self.status.get(status)

    def start_server(self) -> None:
        # Separando string de endereço
        ip, port = self._split_address(self.address)
        # Inicializando servidor
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(5)
        # Aguardando conexões externas
        while True:
            client_socket, client_address = self.server.accept()
            handling = threading.Thread(target=self._handle_message, args=(client_socket,), daemon=True)
            handling.start()

    def send_message(self, target: Peer, message: MessageData) -> Union[str, None]:
        try:
            target_ip, target_port = self._split_address(target.address)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(5)
                client.connect((target_ip, target_port))
                self._increment_clock()
                client.send(message.content.encode("utf-8"))
                response = client.recv(1024).decode("utf-8") 
                print(message.warning)
                client.close()
        except:
            self._set_peer_status(target, False)
            return None
        else:
            self._set_peer_status(target, True)
            return response

    def send_get_peers(self, target: Peer, message: MessageData) -> Union[str, None]:
        response = self.send_message(target, message)
        if not response:
            return
        return response

    def get_peer(self, address: str) -> Union[Peer, None]:
        for peer in self.known_peers:
            if address == peer.address:
                return peer
        return None

    def _handle_message(self, client: socket.socket) -> None:
        message = client.recv(1024).decode("utf-8")
        print(f"""\nMensagem recebida: "{message.replace("\n", "")}" """)
        self._increment_clock()
        splitted_message = message.replace("\n", "").split(" ")
        sender = splitted_message[0]
        message_type = splitted_message[-1]
        response_content = self.handle_type.get(message_type)(sender)
        if response_content:
            response_message = Message.create_response(
                origin=self.address,
                target=sender,
                clock=self.clock,
                type=response_content.get("type"),
                args=response_content.get("args", "")
            )
            print(response_message.warning)
            client.send(response_message.content.encode("utf-8"))
        client.close()
        self.insert_known_peer(sender)

    def _handle_hello(self, *args) -> None:
        return None

    def _handle_get_peers(self, sender: str) -> dict:
        peers = self.known_peers
        peers_number = len(peers)
        response_args = f" "
        for peer in peers:
            if peer.address == sender:
                peers_number -= 1
                continue
            response_args += f"{peer.address}:{peer.status}:0\n"
        return {
            "type": "PEER_LIST",
            "args": f"{peers_number}"+response_args
        }

    def _handle_bye(self, sender: str) -> None:
        peer = self.get_peer(sender)
        self._set_peer_status(peer, False)

    def _increment_clock(self) -> None:
        self.clock += 1
        print(f"=> Atualizando relogio para {self.clock}")

    def _set_peer_status(self, peer: Peer, status: bool) -> None:
        if peer.status != self.status.get(status):
            peer.status = self.status.get(status)
            print(f"Atualizando peer {peer.address} status {self.status[status]}")

    def _split_address(self, address: str) -> tuple:
        split = address.split(":")
        return split[0], int(split[1])
    