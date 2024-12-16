#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importa as bibliotecas necessárias para o funcionamento do script
import paramiko  # Para SSH em servidores remotos
import subprocess  # Para executar comandos no sistema local
import requests  # Para realizar requisições HTTP (não usado diretamente, mas pode ser útil em futuros aprimoramentos)
import telegram  # Para interação com a API do Telegram
import os  # Para acessar variáveis do sistema (caso necessário)
from telegram import Bot  # Para enviar mensagens pelo Telegram

# Configurações do Telegram
TOKEN = 'seu_token_aqui'  # Substitua com seu token do bot do Telegram
CHAT_ID1 = 'seu_chat_id1_aqui'  # Substitua com o ID do chat de um grupo
CHAT_ID2 = 'seu_chat_id2_aqui'  # Substitua com o ID do chat de outro grupo

# Função para executar um comando remoto via SSH em servidores
def executar_comando_ssh(hostname, username, chave_privada, porta, comando):
    # Inicializa a conexão SSH
    client = paramiko.SSHClient()
    try:
        # Carrega as chaves do sistema e define o comportamento em caso de chave desconhecida
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conecta ao servidor remoto
        client.connect(hostname, port=porta, username=username, key_filename=chave_privada)
        
        # Executa o comando e coleta a saída e erro
        stdin, stdout, stderr = client.exec_command(comando)
        saida_comando = stdout.read().decode()  # Saída padrão do comando
        erro_comando = stderr.read().decode()  # Saída de erro do comando

        # Se houver erro na execução, gera uma exceção
        if erro_comando:
            raise Exception(erro_comando)

        # Retorna a saída do comando
        return saida_comando
    except Exception as e:
        # Retorna mensagem de erro em caso de falha
        return f"Erro ao executar o comando SSH em {hostname}: {str(e)}"
    finally:
        # Garante que a conexão SSH seja fechada após a execução
        client.close()

# Função para enviar mensagens para o Telegram
def send_telegram_message(message):
    bot = telegram.Bot(token=TOKEN)  # Cria uma instância do bot do Telegram
    max_message_length = 4096  # Limite de tamanho para uma mensagem no Telegram
    num_messages = len(message) // max_message_length + 1  # Divide a mensagem em partes menores, se necessário

    for i in range(num_messages):
        start = i * max_message_length
        end = start + max_message_length
        part = message[start:end]  # Pega uma parte da mensagem
        # Envia a mensagem para os dois chats
        bot.send_message(chat_id=CHAT_ID1, text=part)
        bot.send_message(chat_id=CHAT_ID2, text=part)

# Lista de hosts (servidores remotos) que serão monitorados
hosts = [
    "endereco_ip_1",  # Substitua pelos endereços IP reais
    "endereco_ip_2",
    "endereco_ip_3",  # Este host usa um comando diferente
    "endereco_ip_4",
    "endereco_ip_5",
    "endereco_ip_6"
]

# Configurações de SSH
username = "seu_usuario_aqui"  # Substitua com seu nome de usuário
chave_privada = "/caminho/para/sua/chave_privada"  # Substitua com o caminho para sua chave privada
porta = 1024  # Porta padrão para SSH
comando_default = "/usr/bin/df -h | /usr/bin/grep 'backup'"  # Comando para verificar o uso de disco
comando_host_especifico = "/usr/bin/df -h | /usr/bin/grep 'home'"  # Comando diferente para um host específico

# Inicializa a variável que armazenará as mensagens a serem enviadas no Telegram
mensagem = "Espaço livre em Storages\n"

# Executa o comando em cada host e processa a resposta
for host in hosts:
    # Verifica se o host exige um comando específico
    if host == "endereco_ip_3":
        comando = comando_host_especifico
    else:
        comando = comando_default

    # Executa o comando via SSH e coleta a saída
    saida_comando = executar_comando_ssh(host, username, chave_privada, porta, comando)

    # Verifica se houve erro ao executar o comando
    if "Erro ao executar o comando SSH" in saida_comando:
        print(saida_comando)  # Loga o erro na tela
        mensagem += f"{host}: {saida_comando}\n"  # Adiciona a mensagem de erro ao relatório
    elif saida_comando:
        # Processa a saída do comando, que contém o uso de disco
        for linha in saida_comando.splitlines():
            partes = linha.split()
            if len(partes) >= 5:
                porcentagem = partes[4]  # Porcentagem de espaço utilizado
                gbs_livres = partes[3]  # Espaço livre em GB
                mensagem += f"{host} -- {porcentagem} utilizado - {gbs_livres} livres\n"
    else:
        erro_msg = f"{host}: Não foi possível alcançar o servidor"
        print(erro_msg)  # Loga o erro na tela
        mensagem += erro_msg + "\n"  # Adiciona a mensagem de erro ao relatório

# Envia o relatório final para o Telegram
send_telegram_message(mensagem)
