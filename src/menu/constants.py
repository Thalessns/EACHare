"""Constantes para o menu do Peer."""

class Constant:
    """Classe para armazenar as constantes do menu do Peer.
    
    Args:
        MAIN_MENU (str): Menu principal do peer.
        LIST_PEERS (str): Menu para listar peers.
        LIST_FILES (str): Menu para listar arquivos locais.
        LIST_FILES_LS (str): Menu para listar arquivos encontrados na rede.
    """
    MAIN_MENU="""
Escolha um comando:
        [1] Listar peers
        [2] Obter peers
        [3] Listar arquivos locais
        [4] Buscar arquivos
        [5] Exibir estatisticas
        [6] Alterar tamanho de chunk
        [9] Sair
-> """

    LIST_PEERS="""
Lista de Peers:
        [0] Voltar para o menu anterior"""

    LIST_FILES="""
Arquivos locais:"""

    LIST_FILES_LS=f"""
Arquivos encontrados na rede:
        {"Nome":^20} | {"Tamanho":^20} | {"Peer":^20}
        {"[0] <Cancelar>":<20} | {"":^20} | {"":^20} """
