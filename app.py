from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from web_scraping import Scraping
from database import iniciar_conexao   
from regressao import modelo_faturamento, grafico_linha

app = FastAPI()
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
    print("API iniciada e conectada ao Firestore")

async def save_db(dados):
    global db
    if db is None:
        raise Exception("A conexão com o Firestore não foi estabelecida.")
    try:
        colecao = db.collection("reclamacoes")
        for dado in dados:
            colecao.add(dado)
        return {"status_code": 200, "mensagem": "Dados coletados e salvos com sucesso", "dados": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao salvar no banco de dados: " + str(e))


@app.get("/scrape/{empresa}")
async def scrape(empresa: str, max_page: int = Query(None, description="Número máximo de páginas para scraping")):
    try:
        scraper = Scraping(empresa, max_page)
        dados = await scraper.iniciar()

        return await save_db(dados)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao realizar web scraping: " +str(e))


@app.get("/reclamacoes/{empresa}")
async def consultar_reclamacoes(empresa: str):
    try:
        print(f"Consultando dados para a empresa: {empresa}")  # Adiciona log para depuração
        colecao = db.collection("reclamacoes")
        query = colecao.where('empresa', '==', empresa)
        docs = query.stream()
        
        dados = []
        for doc in docs:
            doc_data = doc.to_dict()
            print(f"Documento encontrado: {doc_data}")  # Adiciona log para depuração
            dados.append(doc_data)
        
        if not dados:
            return {"status_code": 404, "mensagem": "Nenhuma reclamação encontrada para a empresa especificada."}
        
        return {"status_code": 200, "dados": dados}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar dados: {str(e)}")

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
    import uvicorn
    uvicorn.run(app, log_level="debug")
