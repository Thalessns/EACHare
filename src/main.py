import sys
import threading

from src.menu.service import MenuService
from src.peer.service import PeerService


if __name__ == "__main__":
    # Obtendo parâmetros
    address = sys.argv[1]
    peers_file_path = (sys.argv[2])
    shared_directory = sys.argv[3]

    peer_service = PeerService(address, peers_file_path, shared_directory)
    server_thread = threading.Thread(target=peer_service.start_server, daemon=True)
    server_thread.start()

    menu_service = MenuService(peer_service)
    menu_service.main_menu()