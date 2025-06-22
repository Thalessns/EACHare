import threading
import ast
import base64

from concurrent.futures import ThreadPoolExecutor
from typing import Union, List, Dict
from time import time

from src.peer.service import PeerService
from src.peer.schemas import Peer, SharedFile, MessageType
from src.peer.message import Message, MessageData
from src.menu.constants import Constant
from src.stats.service import manage_stats


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
    
    def send_dl(self, owners: Union[str, List[str]], file: SharedFile) -> Dict[str, any]:
        peers = [self.peer.get_peer(owner) for owner in owners]

        chunk_size = int(self.peer.chunk)
        file_size = int(file.bytes_size)
        
        # Calcula quantos chunks o arquivo possui
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        # Divide os chunks entre os peers disponíveis
        chunks_per_peer = total_chunks // len(peers)
        remaining_chunks = total_chunks % len(peers)
        
        # Dicionário para armazenar as respostas
        responses = {}
        lock = threading.Lock()
        
        chunk_times = {}

        def download_chunks(
            peer: Peer,  
            start_chunk: int, 
            end_chunk: int
        ):
            for chunk_index in range(start_chunk, end_chunk):
                chunk_start_time = time()
                args = f"{file.name} {chunk_size} {chunk_index}"
                response = self._get_peers_responses(
                    peers_list=[peer],
                    message_type=MessageType.DL,
                    args=args,
                    response_data_separation="blankspace"
                )

                with lock:
                    responses[str(chunk_index)] = response[0] if response else None

                chunk_end_time = time() - chunk_start_time
                chunk_times[chunk_index] = chunk_end_time

        # Cria e inicia as threads para cada peer
        chunk_start = 0
        
        # Inicializando contador de tempo
        start_time = time()

        with ThreadPoolExecutor(max_workers=len(peers)) as executor:
            futures = []
            for i, peer in enumerate(peers):
                # Calcula quantos chunks este peer vai processar
                chunks_this_peer = chunks_per_peer + (1 if i < remaining_chunks else 0)
                chunk_end = chunk_start + chunks_this_peer
                
                # Iniciando temporizador do chunk
                chunk_start_time = time()

                # Submete a tarefa ao executor
                futures.append(
                    executor.submit(
                        download_chunks,
                        peer,
                        chunk_start,
                        chunk_end
                    )
                )

                chunk_start = chunk_end
            
            # Espera todas as threads completarem
            for future in futures:
                future.result()

        # Finaliza a contagem de tempo
        total_time = time() - start_time
        # Salvando estatísticas de tempo
        manage_stats.save(
            chunk_size=chunk_size,
            chunk_times=chunk_times.values(),
            num_chunks=total_chunks,
            num_peers=len(peers),
            file_size=file_size,
            total_time=total_time
        )

        # Ordena as respostas pelos índices dos chunks
        sorted_responses = {
            k: responses[k] 
            for k in sorted(responses.keys(), key=lambda x: int(x))
        }
        
        chunks_content = b""

        for index, response in sorted_responses.items():
            file_bytes = base64.b64decode(response["args"][-1])
            chunks_content += file_bytes

        return chunks_content

    def save_shared_file(self, file_name: str, file_content: bytes) -> None:
        status = self.peer.save_shared_file(
            file_name=file_name,
            file_content=file_content
        )
        if status:
            print(f"Download do arquivo {file_name} finalizado.")

    def run_st(self) -> list:
        return manage_stats.get_data()

    def change_chunk_size(self, new_value: int) -> None:
        self.peer.change_chunk_size(new_value)

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
            if len(splited_arg) < 2: continue
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