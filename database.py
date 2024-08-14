import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
def iniciar_conexao():
    # chave_acesso = 'C:/Users/User/Desktop/InsightIA/db_config.json'
    # Obtém as credenciais do ambiente
    database = os.getenv('FIREBASE_CREDENTIALS')

    if database is None:
        raise HTTPException(status_code=500, detail="As credenciais do Firebase não foram encontradas no ambiente.")

    chave_acesso = json.loads(database)
    
    cred = credentials.Certificate(chave_acesso)
    firebase_admin.initialize_app(cred)

    return firestore.client()