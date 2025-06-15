from src.menu.command import Command
from src.menu.constants import Constant
from src.peer.service import PeerService, SharedFile


class MenuService:

    def __init__(self, peer: PeerService) -> None:
        self.commands = Command(peer)
        self.options = {
            1: self._list_peers,
            2: self._get_peers,
            3: self._list_local_files,
            4: self._ls,
            5: self._st,
            6: self._change_chunk_size,
            9: self._exit
        }

    def main_menu(self):
        exit = False
        while not exit:
            try:
                choice = input(Constant.MAIN_MENU)
                if not choice.isdigit():
                    raise ValueError
            except ValueError:    
                print(f"O valor '{choice}' não é uma opção válida!")
            except Exception as error:
                print(f"Erro: {error}")
            else:
                choice = int(choice)
                exit = self.options.get(choice)()

    def _list_peers(self) -> None:
        peers = self.commands.list_peers()
        max_index = len(peers) + 1
        choice = -1
        while True:
            try:
                print(Constant.LIST_PEERS)
                for index, peer in enumerate(peers):
                    print(f"        [{index + 1}] {peer.address} {peer.status} {peer.clock}")
                choice = input("    -> ")
                if not choice.isdigit() or int(choice) not in range(0, max_index):
                    raise ValueError
                choice = int(choice)
            except ValueError:    
                print(f"O valor '{choice}' não é uma opção válida!")
            else:
                if choice == 0:
                    break
                target = peers[choice-1]
                self.commands.send_hello(target)
                peers = self.commands.list_peers()

    def _get_peers(self) -> None:
        self.commands.send_get_peers()

    def _list_local_files(self) -> None:
        self.commands.list_local_files()

    def _ls(self) -> None:
        files = self.commands.send_ls()
        exit = False
        while not exit:
            try:
                print(Constant.LIST_FILES_LS)
                for index, file in enumerate(files):
                    file_owners = ""
                    if len(file["owner"]) > 1:
                        for owner in file['owner']:
                            file_owners += f"{owner}, "
                        file_owners = file_owners[0:-2]
                    else:
                        file_owners = file["owner"][0]
                    print(f"        [{index+1}] {file['name']:<16} | {file['bytes_size']:^20} | {file_owners:<20}")
                choice = input("-> ")
                if not choice.isdigit():
                    raise ValueError
                choice = int(choice)
                if choice not in range(0, len(files)+1):
                    raise ValueError
            except ValueError:
                print(f"O valor '{choice}' não é uma opção válida!")
            else:
                if choice != 0:
                    target = files[choice-1]
                    file_content = self.commands.send_dl(
                        owners=target["owner"],
                        file=SharedFile(
                            name=target["name"],
                            bytes_size=target["bytes_size"]
                        )
                    )
                    self.commands.save_shared_file(
                        file_name=target["name"],
                        file_content=file_content
                    )
                break

    def _st(self) -> None:
        stats_list = self.commands.run_st()
        print("Tam. chunk | N peers | Tam. arquivo | N | Tempo [s] | Desvio")
        for stat in stats_list:
            print(f"{stat.chunk_size:^11}|{stat.num_peers:^9}|{stat.file_size:^14}|{'-':^3}|{stat.time:^11.5f}|{'-':^7}")

    def _change_chunk_size(self) -> None:
        try:
            print("Digite novo tamanho de chunk:")
            new_value = input("> ")
            if not new_value.isdigit():
                raise ValueError
        except ValueError:    
                print(f"O valor '{new_value}' não é uma opção válida!")
        except Exception as error:
            print(f"Erro: {error}")
        else:
            self.commands.change_chunk_size(int(new_value))
            print(f"        Tamanho de chunk alterado: {new_value}")

    def _exit(self) -> bool:
        try:
            self.commands.send_bye()
        except Exception as error:
            print(f"Um erro ocorreu: {error}")
            return False
        else:
            return True
