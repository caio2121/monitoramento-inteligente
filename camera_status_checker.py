#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import requests
import subprocess
import telegram
from telegram import Bot

# Configurações do Telegram
# Substitua a string do token por uma variável de ambiente ou arquivo seguro
TOKEN = 'SEU_TOKEN_AQUI'  # Boa prática: Utilize variáveis de ambiente para armazenar tokens
CHAT_ID = 'SEU_CHAT_ID'  # Boa prática: Armazene o ID do chat em um local seguro
ID_GOOGLESHEETS = 'ID_PLANILHA'
# URL e caminho do arquivo da planilha Google Sheets
google_sheets_url = "https://docs.google.com/spreadsheets/d/ID_GOOGLESHEETS/export?format=csv&gid=0"
additional_csv_path = "/tmp/additional_hosts.csv"  # Caminho onde o CSV da planilha será salvo

# Função para baixar e salvar um arquivo CSV a partir de uma URL
def download_csv(url, path):
    """
    Faz uma requisição HTTP para baixar um arquivo CSV de uma URL e salva no caminho especificado.
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "w", newline="", encoding="utf-8") as file:
            file.write(response.text)

# Função para enviar uma mensagem no Telegram
def send_telegram_message(message):
    """
    Divide a mensagem em partes menores se necessário e envia para o chat do Telegram.
    """
    bot = telegram.Bot(token=TOKEN)
    max_message_length = 4096  # Tamanho máximo permitido pelo Telegram para uma mensagem
    num_messages = len(message) // max_message_length + 1  # Calcula o número de partes necessárias

    for i in range(num_messages):
        start = i * max_message_length
        end = start + max_message_length
        part = message[start:end]

        bot.send_message(chat_id=CHAT_ID, text=part)

# Função para verificar o status de um host (usando fping)
def check_host_status(ip):
    """
    Executa o comando `fping` para verificar se o IP está respondendo.
    Retorna True se o host estiver online e False caso contrário.
    """
    try:
        subprocess.check_output(['/usr/sbin/fping', '-c', '1', ip], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

# Função principal
def main():
    """
    Coordena o fluxo de execução:
    1. Baixa o arquivo CSV da planilha do Google Sheets.
    2. Verifica o status dos hosts.
    3. Gera um relatório e envia via Telegram.
    """
    # Baixa o arquivo CSV da planilha do Google Sheets
    download_csv(google_sheets_url, additional_csv_path)

    offline_hosts = []

    # Verifica o status dos hosts listados no arquivo da planilha
    with open(additional_csv_path, 'r', encoding='utf-8') as add_csvfile:
        add_csvreader = csv.reader(add_csvfile)
        next(add_csvreader)  # Pula o cabeçalho
        for row in add_csvreader:
            if len(row) >= 2:  # Certifica-se de que a linha possui colunas suficientes
                ip, name = row[0].strip(), row[1].strip()
                if not check_host_status(ip):
                    offline_hosts.append(f"{name}: {ip} está offline")

    # Envia o relatório
    if offline_hosts:
        message = f'Câmeras Offline/Falhando\nTotal: {len(offline_hosts)}\n\n' + '\n'.join(offline_hosts)
        send_telegram_message(message)
    else:
        send_telegram_message('Todos os dispositivos estão online!')

if __name__ == '__main__':
    main()
