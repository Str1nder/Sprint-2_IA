import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
def iniciar_conexao():
    # Caminho para o seu arquivo de credenciais JSON
    # chave_acesso = 'C:/Users/User/Desktop/InsightIA/db_config.json'
    # Obtém as credenciais do ambiente
    database = os.getenv('FIREBASE_CREDENTIALS')

    if database is None:
        raise ValueError("As credenciais do Firebase não foram encontradas no ambiente.")

    # Converte a string JSON para um dicionário
    chave_acesso = json.loads(database)
    
    # Inicializa o Firebase com as credenciais fornecidas
    cred = credentials.Certificate(chave_acesso)
    firebase_admin.initialize_app(cred)

    # Retorna a instância do Firestore
    return firestore.client()