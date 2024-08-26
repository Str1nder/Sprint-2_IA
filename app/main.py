import uvicorn
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import iniciar_conexao, set_db, get_db
from app.controllers.scrapping.scrapping_controller import router as scrapping_router
from app.controllers.insights.insights_controller import router as insights_controller

load_dotenv()

appApi = FastAPI(
    title="API InsightIA",
    description="API para realizar web scraping no ReclameAqui, Analise de faturamento e Insight das reclamacoes",
    version="0.8.1",
    docs_url="/doc",  # Customiza a URL do Swagger
    openapi_url="/openapi.json",  # Customiza a URL do JSON do OpenAPI
)

appApi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@appApi.on_event("startup")
async def startup_event():
    db = iniciar_conexao()
    set_db(db)

appApi.include_router(scrapping_router)
appApi.include_router(insights_controller)

if __name__ == "__main__":
    uvicorn.run(appApi, log_level="debug")
