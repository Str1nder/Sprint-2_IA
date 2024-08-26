import os
import json
import firebase_admin
from fastapi import HTTPException
from firebase_admin import credentials, firestore, auth

def iniciar_conexao():
    firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_credentials is None:
        raise HTTPException(status_code=500, detail="Não foi possível se conectar ao firebase.")

    try:
        chave_acesso = json.loads(firebase_credentials)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao decodificar JSON: {str(e)}")

    cred = credentials.Certificate(chave_acesso)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def set_db(database):
    global db
    db = database

def get_db():
    return db
