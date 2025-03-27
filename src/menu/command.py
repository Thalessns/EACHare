from typing import List
from os import listdir

from src.peer.service import PeerService
from src.peer.schemas import Peer
from src.peer.message import Message
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
        peers_list = self.list_peers()
        responses_content = []
        for peer in peers_list:
            message = Message.create(
                origin=self.peer.address,
                clock=self.peer.clock,
                target=peer.address,
                type="GET_PEERS"
            )
            response_content = self.peer.send_get_peers(peer, message)
            if not response_content:
                continue
            responses_content.append(response_content)
        responses = []
        for content in responses_content:
            Message.show_response_warning(content)
            self.peer._increment_clock()
            response_dict = self._get_reponse_dict(content)
            responses.append(response_dict)
        for response in responses:
            peer_list = self._prepare_get_peers_response_args(response.get("args"))
            for peer in peer_list:
                self.peer.insert_known_peer(
                    new_peer=peer.get("address"),
                    status=peer.get("status")
                )  

    def list_local_files(self) -> None:
        print(Constant.LIST_FILES)
        for file in listdir(self.peer.shared_directory):
            print(f"- {file}")

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

    def _get_reponse_dict(self, response: str) -> dict:
        splitted_response = response.split(" ")
        response_dict = {
            "sender": splitted_response[0],
            "sender_clock": splitted_response[1],
            "type": splitted_response[2],
            "args": None
        }
        if len(splitted_response) > 4:
            args = splitted_response[4].replace("\n\n", "").replace("\n", " ").split(" ")
            response_dict["args"] = args
        return response_dict
    
    def _prepare_get_peers_response_args(self, args: List[str]) -> List[dict]:
        result = []
        for arg in args:
            splited_arg = arg.split(":")
            result.append(
                {
                    "address": splited_arg[0]+":"+splited_arg[1],
                    "status": (True if splited_arg[2] == "ONLINE" else False),
                    "number": splited_arg[3]
                }
            )
        return result