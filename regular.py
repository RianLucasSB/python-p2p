import xmlrpc.client
import xmlrpc.server
import xmlrpc
import logging
import os
import base64
import threading
import hashlib
from pathlib import Path

PORTA_BORDA = "8000"
PORTA = 9000
ENDERECO_COMPLETO = f"http://192.168.100.5:{PORTA}"

logging.basicConfig(level=logging.INFO)

# Servidor do próprio nó
server_regular = xmlrpc.server.SimpleXMLRPCServer(('localhost', PORTA), allow_none=True, logRequests=False)

# Conexão com o nó borda
server = xmlrpc.client.ServerProxy(f"http://3.80.212.41")


def checksum(nome_arquivo):
    with open(nome_arquivo, 'rb') as f:
        dados_do_arquivo = f.read()
        md5 = hashlib.md5()
        md5.update(dados_do_arquivo)
        return md5.hexdigest()


def upload_arquivo(nome_arquivo, endereco_noh_receptor):
    path_arquivo = f"{Path.cwd()}/{nome_arquivo}"
    with open(path_arquivo, "rb") as f:
        dados_arquivo = f.read()
    file_name = os.path.basename(path_arquivo)
    conexao_noh_receptor = xmlrpc.client.ServerProxy(endereco_noh_receptor)
    result = conexao_noh_receptor.recebe_arquivo(file_name, base64.b64encode(dados_arquivo).decode("utf-8"))
    print(result)


def recebe_arquivo(nome_arquivo, dados_arquivo):
    with open(nome_arquivo, "wb") as f:
        f.write(base64.b64decode(dados_arquivo))
    return f"Sucesso! Foi feito o upload do arquivo: {nome_arquivo}."


def retorna_arquivos(lista):
    print(lista)
    lista_de_arquivos = lista
    for arquivo in os.listdir("/files"):
        print(arquivo)
        if(arquivo == ".idea"):
            continue
        arquivo_na_pasta = [arquivo, ENDERECO_COMPLETO, checksum(arquivo)]
        if (arquivo_na_pasta not in lista_de_arquivos):
            lista_de_arquivos.append(arquivo_na_pasta)
    return lista_de_arquivos


server_regular.register_function(retorna_arquivos, "retorna_arquivos")
server_regular.register_function(upload_arquivo, "upload_arquivo")
server_regular.register_function(recebe_arquivo, "recebe_arquivo")


# Inicializa o servidor
def inicializa_servidor():
    logging.info(f" Nó regular inicialiado na porta {server_regular.server_address[1]}...")
    server.envia_endereco(ENDERECO_COMPLETO)
    server_regular.serve_forever()


# Cliente escolhe o que fazer
def escolher():
    while True:
        print("\n[0] - Solicitar arquivo\n[-1] - Sair da aplicação\n")
        escolha = input()
        if (escolha == "0"):
            nome_arquivo_escolhido = input("Digite o nome do arquivo: ")
            lista = server.envia_localizacao_arquivo(nome_arquivo_escolhido)
            if len(lista) == 0:
                print("Arquivo não encontrado.")
            else:
                print("Nós com o arquivo:\n")
                for endereco in lista:
                    print(f"-> {endereco}")
                conexao_regular = xmlrpc.client.ServerProxy(lista[0])
                conexao_regular.upload_arquivo(nome_arquivo_escolhido, ENDERECO_COMPLETO)

        elif escolha == "-1":
            break


server_thread = threading.Thread(target=inicializa_servidor)
server_thread.start()

escolha_thread = threading.Thread(target=escolher)
escolha_thread.start()
