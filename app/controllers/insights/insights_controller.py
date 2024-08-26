from fastapi import FastAPI, Query, HTTPException, File, UploadFile, APIRouter
from .prompts import criar_question
from app.database.connection import get_db

router = APIRouter()

# o que eu vou retornar aqui:
# porcentagem de cada categoria de problema que vai ser mostrado em gráfico
# possíveis causas / soluções para cada categoria
# email para ser enviado ao máximo de reclamações possíveis relacionado a categoria
@router.post("/insight/interno")
async def gerar_insight_interno(uuid: str, empresa: str):
    try:
      db = get_db()
      if db is None:
        raise HTTPException(status_code=500, detail="A conexão com o Firestore não foi estabelecida")
      empresa = empresa.replace(' ', '-')
      
      user_document = db.collection("dadosUsuarios").document(uuid)
      doc = user_document.get()
      if not doc.exists:
          raise HTTPException(status_code=404, detail=f"Usuário com UUID {uuid} não encontrado.")
      user_data = doc.to_dict()
      
      historico = user_data.get("historico", [])
      empresa_dados = next((item for item in historico if empresa in item), None)
      if empresa_dados is None:
          raise HTTPException(status_code=404, detail=f"Nenhuma reclamação encontrada para a empresa {empresa}.")
      dados = empresa_dados.get(empresa, [])
      print(dados["dados"]["dados"])
      
      response = criar_question(dados["dados"]["dados"])
      return { "status_code": 200, "análise_por_categoria": response }
    
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/insight/concorrente")
async def gerar_insight_concorrente(uuid: str, empresa_interna: str, empresa_externa: str):
  ...