import sys
import requests
import json

# Verificar se os parâmetros foram passados
if len(sys.argv) != 3:
    print("Por favor, forneça o título e o conteúdo do ticket.")
    sys.exit(1)

# Receber os parâmetros do título e conteúdo
ticket_name = sys.argv[1]
ticket_content = sys.argv[2]

# URL para autenticação (iniciar sessão)
glpi_url = "https://glpi.com.br/apirest.php/initSession"

# Defina os tokens
user_token = ""  # Substitua com seu token pessoal
app_token = ""    # Substitua com seu token da aplicação

# Dados para autenticação
headers = {
    "App-Token": app_token,
    "Authorization": f"user_token {user_token}"
}

# Enviar a requisição POST para iniciar a sessão e obter o Session-Token
response = requests.post(glpi_url, headers=headers)

# Verificar a resposta e obter o Session-Token
if response.status_code == 200:
    session_token = response.json().get('session_token')  # Alterado para acessar o valor correto
    print("Sessão iniciada com sucesso!")
else:
    print(f"Erro ao iniciar sessão: {response.status_code}")
    print(response.text)
    sys.exit(1)

# URL para criar o ticket
ticket_url = "https://glpi.com.br/apirest.php/Ticket"

# Cabeçalhos de autenticação com o Session-Token obtido
headers = {
    "Content-Type": "application/json",
    "Session-Token": session_token,
    "App-Token": app_token
}

# Dados do ticket que será criado
ticket_data = {
    "input": {
        "name": ticket_name,
        "content": ticket_content,
        "itilcategories_id": 7,   # Substitua com o ID correto da categoria
        "requesttypes_id": 1,     # Substitua com o ID correto do tipo de solicitação
        "urgency": 3,             # Urgência do chamado (1-5)
        "impact": 2,              # Impacto do chamado (1-5)
        "status": 1               # Status do ticket (1 para "Novo")
    }
}

# Enviar a requisição POST para criar o ticket
response = requests.post(ticket_url, headers=headers, json=ticket_data)

# Verificar a resposta
if response.status_code == 201:
    print("Ticket criado com sucesso!")
    print("Detalhes do ticket:", response.json())
else:
    print(f"Erro ao criar ticket: {response.status_code}")
    print(response.json())
