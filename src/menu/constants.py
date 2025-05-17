
class Constant:

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