# Importando as bibliotecas necessárias
import csv  # Para leitura e escrita de arquivos CSV
import unicodedata  # Para manipulação de caracteres Unicode
import re  # Para trabalhar com expressões regulares
from pyzabbix import ZabbixAPI, ZabbixAPIException  # Para interagir com a API do Zabbix
from datetime import datetime  # Para manipulação de data e hora

# Conectar à API do Zabbix
zabbix_server = 'http://zabbix.com/'  # URL do servidor Zabbix
zabbix_user = 'apicameras'  # Usuário de autenticação na API (não colocar credenciais em código)
zabbix_password = 'SUA_SENHA_AQUI'  # Senha de autenticação (utilizar variáveis de ambiente ou gerenciadores de segredo)

# Conexão com a API do Zabbix
zapi = ZabbixAPI(zabbix_server)  # Cria uma instância da API do Zabbix
zapi.login(zabbix_user, zabbix_password)  # Realiza o login utilizando as credenciais fornecidas

# Caminhos para os arquivos CSV e de log
CSV_FILE = '/tmp/csvcameras.csv'  # Caminho do arquivo CSV com dados dos hosts
LOG_FILE = '/tmp/logfilecameras.txt'  # Caminho do arquivo de log para registrar erros

# Obtendo a data e hora atuais para registrar no log
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato para data e hora

# Função para sanitizar nomes de hosts (remover caracteres inválidos)
def sanitize_host_name(host_name):
    # Substitui caracteres não alfanuméricos (exceto ponto e sublinhado) por '_', garantindo nomes válidos
    return re.sub(r'[^a-zA-Z0-9._]', '_', host_name)

# Função para registrar mensagens de erro em um arquivo de log
def log_error(message):
    # Abre o arquivo de log em modo de anexação e escreve a mensagem de erro
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')  # Adiciona a mensagem de erro no log

# IDs de grupo e template (substitua pelos valores corretos para o seu ambiente)
group_id = '295'  # ID do grupo de hosts (ajustar conforme necessário)
template_id = '28134'  # ID do template de host (ajustar conforme necessário)

# Leitura do arquivo CSV contendo as informações dos hosts
with open(CSV_FILE, 'r', encoding='utf-8') as csvfile:
    # Lê o arquivo CSV com separador de ponto e vírgula
    csvreader = csv.reader(csvfile, delimiter=';')
    next(csvreader)  # Pula a primeira linha (cabeçalho)

    # Processa cada linha do CSV
    for row in csvreader:
        # Obtém o código, nome, IP, descrição e status do host a partir da linha do CSV
        code = row[0].strip("'")  # Código do host, removendo aspas se existirem
        host_name = sanitize_host_name(row[1])  # Sanitiza o nome do host
        host_ip = row[7]  # IP do host
        description = row[2]  # Descrição do host
        status_text = row[8].lower()  # Texto do status, converte para minúsculas

        # Convertendo o status do host para o formato aceito pelo Zabbix (1 para desligada, 0 para ligada)
        status_value = 1 if status_text == 'desligada' else 0  # 1 para desligada, 0 para ligada

        host_name = f"{code}--{host_name}"  # Formatação final do nome do host, incluindo código

        try:
            # Verificar se o host já existe no Zabbix
            hosts = zapi.host.get(filter={"host": host_name})

            if hosts:  # Se o host já existir no Zabbix
                # Obtém o hostid e os dados do host
                host_id = hosts[0]['hostid']
                current_name = hosts[0]['host']
                current_status = int(hosts[0]['status'])

                # Atualiza o nome do host se necessário
                if current_name != host_name:
                    zapi.host.update({
                        'hostid': host_id,  # ID do host a ser atualizado
                        'host': host_name  # Novo nome do host
                    })

                # Atualiza o status do host se necessário
                if current_status != status_value:
                    zapi.host.update({
                        'hostid': host_id,  # ID do host a ser atualizado
                        'status': status_value  # Novo status do host
                    })
            else:
                # Se o host não existir, cria um novo host no Zabbix
                try:
                    result = zapi.host.create({
                        'host': host_name,  # Nome do host
                        'interfaces': [{
                            'type': 1,  # Tipo de interface (1 para interface de rede)
                            'main': 1,  # Marca a interface como principal
                            'useip': 1,  # Usar IP para comunicação
                            'ip': host_ip,  # IP do host
                            'dns': '',  # DNS do host (vazio)
                            'port': '10050'  # Porta do Zabbix agent
                        }],
                        'groups': [{'groupid': group_id}],  # Grupo de hosts ao qual o host pertence
                        'templates': [{'templateid': template_id}],  # Template a ser atribuído ao host
                        'status': status_value,  # Status do host
                        'description': description  # Descrição do host
                    })
                except ZabbixAPIException as e:
                    # Caso ocorra erro ao criar o host, registra no log
                    log_error(f"[{now}]Erro ao criar host {host_name}: {e}")

        except ZabbixAPIException as e:
            if 'No permissions to referred object or it does not exist!' in str(e):
                # Caso não tenha permissão ou o host não exista, tenta criar o host
                try:
                    result = zapi.host.create({
                        'host': host_name,  # Nome do host
                        'interfaces': [{
                            'type': 1,  # Tipo de interface (1 para interface de rede)
                            'main': 1,  # Marca a interface como principal
                            'useip': 1,  # Usar IP para comunicação
                            'ip': host_ip,  # IP do host
                            'dns': '',  # DNS do host (vazio)
                            'port': '10050'  # Porta do Zabbix agent
                        }],
                        'groups': [{'groupid': group_id}],  # Grupo de hosts ao qual o host pertence
                        'templates': [{'templateid': template_id}],  # Template a ser atribuído ao host
                        'status': status_value,  # Status do host
                        'description': description  # Descrição do host
                    })
                except ZabbixAPIException as e:
                    # Caso ocorra erro ao criar o host, registra no log
                    log_error(f"[{now}]Erro ao criar host {host_name}: {e}")
            else:
                # Se o erro for diferente, registra no log
                log_error(f"[{now}]Erro ao criar host {host_name}: {e}")
