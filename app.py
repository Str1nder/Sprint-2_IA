import uvicorn
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from web_scraping import Scraping
from database import iniciar_conexao   
from regressao import modelo_faturamento, grafico_linha

app = FastAPI(
    title="API InsightIA",
    description="API para realizar web scraping no ReclameAqui, Analise de faturamento e Insight das reclamacoes",
    version="0.8.1",
    docs_url="/doc",  # Customiza a URL do Swagger
    openapi_url="/openapi.json",  # Customiza a URL do JSON do OpenAPI
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None

@app.on_event("startup")
async def startup_event():
    global db
    db = iniciar_conexao()

async def save_db(dados):
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="A conexão com o Firestore não foi estabelecida")
    try:
        colecao = db.collection("reclamacoes")
        for dado in dados:
            colecao.add(dado)
        return {"status_code": 200, "mensagem": "Dados coletados e salvos com sucesso", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {str(e)}")


@app.get("/")
async def hello_world():
    return {"status_code": 200, "mensagem": "Bem Vindo ao InsightIA"}

# Realizar WebScraping no ReclameAqui buscando a empresa selecionada
@app.get("/scraping/{empresa}")
async def web_scraping(empresa: str, max_page: int = Query(None, description="Número máximo de páginas para scraping")):
    try:
        empresa = empresa.replace(' ', '-')
        scraper = Scraping(empresa, max_page)
        status, dados = await scraper.iniciar()
        
        # Verifica o código de status e faz o retorno apropriado
        if status['status_code'] == 200:
            return await save_db(status['dados'])
        else:
            raise HTTPException(status_code=status['status_code'], detail=f"{status['mensagem']}")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao realizar web scraping: " +str(e))

# Realizar WebScraping no ReclameAqui buscando a empresa selecionada
@app.get("/empresas/")
async def consultar_empresa():
    try:
        dados = {doc.to_dict().get("empresa") for doc in db.collection("reclamacoes").stream()}
        if not dados:
            raise HTTPException(status_code=404, detail=f"Nenhuma empresa com reclamações encontrada.")
        
        return {"status_code": 200, "Empresas": [dados] }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar empresas:  {str(e)}")

@app.get("/reclamacoes/{empresa}")
async def consultar_reclamacoes(empresa: str):
    empresa = empresa.replace(' ', '-')
    try:
        dados = [doc.to_dict() for doc in db.collection("reclamacoes").where('empresa', '==', empresa).stream()]
        if not dados:
            raise HTTPException(status_code=404, detail=f"Nenhuma reclamação encontrada para a empresa informada.")

        return {"status_code": 200, "dados": dados}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar dados: {str(e)}")

@app.delete("/reclamacoes/")
def apagar_todas_reclamacoes():
    try:
        docs = db.collection("reclamacoes").stream()
        for doc in docs:
            doc.reference.delete()

        return {"status_code": 200, "mensagem": "Todas as reclamações foram apagadas com sucesso."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletear os dados: {str(e)}")


@app.post("/faturamento")
async def faturamento(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um arquivo Excel (.xlsx)")
    
    try:
        df = pd.read_excel(file.file)
        pred = modelo_faturamento(df)

        img1_str = grafico_linha(df, 'Receita bruta', pred['X_test'], pred['pred_receita'], pred['intervalo_confianca_receita'])
        img2_str = grafico_linha(df, 'Despesas', pred['X_test'], pred['pred_despesa'], pred['intervalo_confianca_despesa'])

        # Gráfico combinado
        plt.figure(figsize=(12, 6))
        plt.plot(df['Datas'], df['Receita bruta'], label='Receita Bruta Real', color='blue')
        plt.plot(df['Datas'].iloc[pred['X_test'].index], pred['pred_receita'], label='Receita Bruta Prevista', linestyle='--', color='green')
        plt.fill_between(df['Datas'].iloc[pred['X_test'].index], pred['pred_receita'] - pred['intervalo_confianca_receita'], pred['pred_receita'] + pred['intervalo_confianca_receita'], color='blue', alpha=0.2)
        plt.plot(df['Datas'], df['Despesas'], label='Despesas Reais', color='red')
        plt.plot(df['Datas'].iloc[pred['X_test'].index], pred['pred_despesa'], label='Despesas Previstas', linestyle='--', color='purple')
        plt.fill_between(df['Datas'].iloc[pred['X_test'].index], pred['pred_despesa'] - pred['intervalo_confianca_despesa'], pred['pred_despesa'] + pred['intervalo_confianca_despesa'], color='red', alpha=0.2)
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.title('Receita e Despesas Reais vs Previstas com Intervalos de Confiança')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='svg')
        buf.seek(0)
        img3_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        response = {
            'graphs': [
                {'url': f'data:image/svg+xml;base64,{img3_str}'},
                {'url': f'data:image/svg+xml;base64,{img1_str}'},
                {'url': f'data:image/svg+xml;base64,{img2_str}'}
            ]
        }
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, log_level="debug")
