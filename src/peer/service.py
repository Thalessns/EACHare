import socket
import threading
import base64

from os import listdir, stat
from typing import Union, List, Dict

from src.peer.message import MessageData, Message
from src.peer.schemas import Peer, SharedFile


class PeerService:

    def __init__(self, address: str, peers_file_path: str, shared_directory: str) -> None:
        self.status = {
        True: "ONLINE",
        False: "OFFLINE"
        }
        self.handle_type = {
            "HELLO": self._handle_hello,
            "GET_PEERS": self._handle_get_peers,
            "LS": self._handle_ls,
            "DL": self._handle_dl,
            "BYE": self._handle_bye
        }
        self.clock = 0
        self.address = address
        self.peers_file_path = peers_file_path
        self.shared_directory = shared_directory if shared_directory[-1] != "/" else shared_directory[:-1]
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
    
    def insert_known_peer(self, new_peer: str, status: bool = True, current_clock: int = 0) -> None:
        target = self.get_peer(new_peer) 
        if not target:
            Message.show_new_peer(new_peer, self.status.get(status))
            with open(self.peers_file_path, "a") as file:
                file.write(new_peer+"\n")
                file.close()
            target = Peer(
                address=new_peer, 
                status=self.status.get(status), 
                clock=current_clock
            )
            self.known_peers.append(target)
        if current_clock > target.clock:
            target.status = self.status.get(status)
            target.clock = current_clock

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
                self._increment_clock()
                Message.show_sent_warning(message)
                client.connect((target_ip, target_port))
                client.send(message.content.encode("utf-8"))
                response = client.recv(1024).decode("utf-8") 
                client.close()
        except:
            self._set_peer_status(target, False)
            return None
        else:
            if message.type != "BYE": self._set_peer_status(target, True)
            return response

    def get_peer(self, address: str) -> Union[Peer, None]:
        for peer in self.known_peers:
            if address == peer.address:
                return peer
        return None

    def list_files_stats(self) -> List[SharedFile]:
        shared_files = []
        for file in listdir(self.shared_directory):
            file_bytes = stat(f"{self.shared_directory}/{file}").st_size
            shared_files.append(SharedFile(
                name=file,
                bytes_size=file_bytes
            ))
        return shared_files

    def save_shared_file(self, file_name: str, file_content: bytes) -> bool:
        with open(f"{self.shared_directory}/{file_name}", "wb") as new_file:
            file_bytes = base64.b64decode(file_content)
            new_file.write(file_bytes)
            new_file.close()
        return True

    def _handle_message(self, client: socket.socket) -> None:
        message = client.recv(1024).decode("utf-8")
        Message.show_receive_warning(message)
        splitted_message = message.replace("\n", "").split(" ")
        sender = splitted_message[0]
        sender_clock = int(splitted_message[1])
        message_type = splitted_message[2]
        args = None
        if len(splitted_message) > 3:
            args = splitted_message[3:]
        self._set_max_clock_value(sender_clock)
        self._increment_clock()
        self.insert_known_peer(
            new_peer=sender,
            current_clock=sender_clock
        )
        response_content = self.handle_type.get(message_type)(sender, args)
        if response_content:
            self._increment_clock()
            response_message = Message.create(
                origin=self.address,
                target=sender,
                clock=self.clock,
                type=response_content.get("type"),
                args=response_content.get("args", "")
            )
            Message.show_sent_warning(response_message)
            client.send(response_message.content.encode("utf-8"))
        client.close()

    def _handle_hello(self, *args) -> None:
        return None

    def _handle_get_peers(self, sender: str, *args) -> Dict[str, str]:
        peers = self.known_peers
        peers_number = len(peers)
        args = f"{peers_number} "
        for peer in peers:
            if peer.address == sender:
                peers_number -= 1
                continue
            args += f"{peer.address}:{peer.status}:{peer.clock}\n"
        return {
            "type": "PEER_LIST",
            "args": args
        }
    
    def _handle_ls(self, *args) -> Dict[str, str]:
        files = self.list_files_stats()
        args = f"{len(files)} "
        for file in files:
            args += f"{file.name}:{file.bytes_size}\n"
        return {
            "type": "LS_LIST",
            "args": args
        }
    
    def _handle_dl(self, sender: str, *args) -> Dict[str, any]:
        file_name = args[0][0]
        int_1 = args[0][1]
        int_2 = args[0][2]
        encoded_file: bytes
        with open(
            f"{self.shared_directory}/{file_name}", "rb") as file:
            content = file.read()
            encoded_file = base64.b64encode(content)
            file.close()
        args = f"{file_name} {int_1} {int_2} {encoded_file}"
        return {
            "type": "FILE",
            "args": args
        }

    def _handle_bye(self, sender: str, *args) -> None:
        peer = self.get_peer(sender)
        self._set_peer_status(peer, False)

    def _set_max_clock_value(self, sender_clock: int) -> None:
        self.clock = max(self.clock, sender_clock)

    def _increment_clock(self) -> None:
        self.clock += 1
        Message.show_clock_update(self.clock)

    def _set_peer_status(self, peer: Peer, status: bool) -> None:
        peer.status = self.status.get(status)
        Message.show_status_update(peer.address, self.status.get(status))

    def _split_address(self, address: str) -> tuple:
        split = address.split(":")
        return split[0], int(split[1])
    