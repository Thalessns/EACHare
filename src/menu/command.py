from typing import Union, List, Dict

from src.peer.service import PeerService
from src.peer.schemas import Peer, SharedFile, MessageType
from src.peer.message import Message, MessageData
from src.menu.constants import Constant


class Command:

    def __init__(self, peer: PeerService) -> None:
        self.peer = peer

    def list_peers(self) -> List[Peer]:
        return self.peer.known_peers
        
    def send_hello(self, target: Peer) -> None:
        message = Message.create(
                origin=self.peer.address,
                clock=self.peer.clock + 1,
                type="HELLO",
                target=target.address
            )
        self.peer.send_message(target, message)

    def send_get_peers(self) -> None:
        responses = self._get_peers_responses(
            peers_list=self.list_peers(),
            message_type=MessageType.GET_PEERS
        )
        for response in responses:
            peer_list = self._prepare_get_peers_response_args(response.get("args"))
            for peer in peer_list:
                self.peer.insert_known_peer(
                    new_peer=peer.get("address"),
                    status=peer.get("status"),
                    current_clock=int(peer.get("clock"))
                )  

    def list_local_files(self) -> None:
        print(Constant.LIST_FILES)
        for file in self.peer.list_files_stats():
            print(f" - {file.name}")

    def send_ls(self) -> Union[List[Dict], List]:
        online_peers = []
        for peer in self.list_peers():
            if peer.status == "ONLINE":
                online_peers.append(peer)
        responses = self._get_peers_responses(
            peers_list=online_peers,
            message_type=MessageType.LS
        )
        files_mapping = {}
        for response in responses:
            response_files = self._prepare_ls_response_args(response.get("args"))
            for file in response_files:
                if file.name in files_mapping.keys():
                    files_mapping[file.name]["owner"].append(response.get("sender"))
                else:
                    files_mapping[file.name] = {
                    "name": file.name,
                    "bytes_size": file.bytes_size,
                    "owner": [response.get("sender")]
                }
        return [files_mapping[key] for key in files_mapping.keys()]

    def send_dl(self, owner: str, file_name: str) -> Dict[str, any]:
        peer = self.peer.get_peer(owner)
        response = self._get_peers_responses(
            peers_list=[peer],
            message_type=MessageType.DL,
            args=f"{file_name} 0 0",
            response_data_separation="blankspace"
        )
        return response[0]

    def save_shared_file(self, file_name: str, file_content: bytes) -> None:
        status = self.peer.save_shared_file(
            file_name=file_name,
            file_content=file_content
        )
        if status:
            print(f"Download do arquivo {file_name} finalizado.")

    def send_bye(self) -> None:
        online_peers = []
        for peer in self.list_peers():
            if peer.status == "ONLINE":
                online_peers.append(peer)
        for peer in online_peers:
            message = Message.create(
                origin=self.peer.address,
                clock=self.peer.clock,
                type="BYE",
                target=peer.address
            )
            self.peer.send_message(peer, message)
        self.peer.server.close()

    def _send_message(
            self, 
            target: Peer, 
            message: MessageData
        ) -> Union[str, None]:
        return self.peer.send_message(target, message)

    def _get_peers_responses(
            self, 
            peers_list: List[Peer], 
            message_type: MessageType,
            args: str = "",
            response_data_separation: str = "breaklines"
        ) -> Union[List[Dict], List]:
        responses_content = []
        for peer in peers_list:
            message = Message.create(
                origin=self.peer.address,
                clock=self.peer.clock + 1,
                target=peer.address,
                type=message_type.value,
                args=args
            )
            response_content = self._send_message(peer, message)
            if not response_content:
                continue
            responses_content.append(response_content)
        responses = []
        for content in responses_content:
            Message.show_response_warning(content)
            self.peer._increment_clock()
            response_dict = self._get_response_data(
                content,
                response_data_separation
            )
            responses.append(response_dict)
        return responses
    
    def _prepare_get_peers_response_args(self, args: List[str]) -> List[Dict]: 
        result = []
        for arg in args:
            splited_arg = arg.split(":")
            result.append(
                {
                    "address": splited_arg[0]+":"+splited_arg[1],
                    "status": (True if splited_arg[2] == "ONLINE" else False),
                    "clock": splited_arg[3]
                }
            )
        return result

    def _prepare_ls_response_args(self, args) -> Union[List[SharedFile], List]:
        result = []
        for arg in args:
            if arg == "":
                break
            splitted_arg = arg.split(":")
            result.append(
                SharedFile(
                    name=splitted_arg[0],
                    bytes_size=splitted_arg[1]
                )
            )
        return result

    def _get_response_data(self, response: str, method: str) -> Dict[str, any]:
        splitted_response = response.split(" ")
        response_dict = {
            "sender": splitted_response[0],
            "sender_clock": splitted_response[1],
            "type": splitted_response[2],
            "args": []
        }
        if len(splitted_response) > 4:
            if method == "breaklines":
                args = splitted_response[4].replace("\n\n", "").replace("\n", " ").split(" ")
            elif method == "blankspace":
                args = splitted_response[4:]
            response_dict["args"] = args
        return response_dict