from fastapi import HTTPException

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# AUTH FOR GEMINI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# model = genai.GenerativeModel('gemini-1.5-flash') - isso aq é pra gerar o gemini-1.5-flash uma versao pior doq o pro
generation_config = {
  "temperature": 0.2,
  "top_p": 0.8,
  "top_K": 64,
  "max_output_tokens": 100
}
model = genai.GenerativeModel('gemini-1.5-flash')

#empresa, setor, categoria_problema, reclamacoes
def criar_question(dados): 
    if not dados:
        raise ValueError("Dados não fornecidos ou vazios.")

    result = []
    categorias_problema = []
    response_all_categories = []
        
    try:
        for categoria_data in dados:
            empresa = categoria_data["reclamacoes"][0]["empresa"] if categoria_data.get("reclamacoes") else "Desconhecida"
            setor = "Bancos e Financeiras"
            categoria_problema = categoria_data.get("categoria", "Categoria não especificada")
            reclamacoes = [reclamacao["descricao"] for reclamacao in categoria_data.get("reclamacoes", [])]

            categorias_problema.append(categoria_problema)
            if not reclamacoes:
                continue 

            complaints_text = ',\n'.join([f"'{reclamacao}'" for reclamacao in reclamacoes])

            main_question = (
                f"Possuo essas reclamações, na categoria de problema '{categoria_problema}', "
                f"abaixo acerca de uma empresa chamada {empresa} que está no setor de {setor}:\n\n"
                f"{complaints_text}\n\n"
                "Analise as reclamações pensando na categoria de problema que ela está inserida e resuma para mim.\n"
                "Em seguida liste para mim, ao menos, 5 possíveis causas e soluções, de forma geral, dos problemas ditos.\n"
                "Gere para mim um email de resposta geral para essa categoria, de forma a retornar para o cliente o mais rápido possível alguma informação, no seguinte formato:\n\n"
                "' Prezado(a) cliente, já estamos analisando o seu problema.\n\n"
                "  [descricao geral do problema]\n\n"
                "  Para melhora mais fácil em relação ao seu problema, por favor me envie com mais detalhes\n"
                "  [peça dados do cliente para atendimento privado]\n\n"
                f"  Atenciosamente,\n  {empresa}\n"
                "'"
            )

            main_response = model.generate_content(main_question)

            response_all_categories.append(main_response)


        for index, response_categorie in response_all_categories:
            unit_categorie_analise_text = (
                "Abaixo está um texto que você mesmo me gerou. \n"
                f"me retorne apenas o texto relacionado a análise das reclamações da categoria do problema '{categorias_problema[index]}' que ela está inserida\n\n"
                f"{response_categorie}"
                "'"
            )

            unit_categorie_analise_text_response = model.generate_content(unit_categorie_analise_text)

            unit_categorie_causa_solucao_text = (
                "Abaixo está um texto que você mesmo me gerou. \n"
                f"me retorne apenas o texto relacionado das listagem das possíveis causas e soluções dos problemas ditos\n\n"
                f"{response_categorie}"
                "'"
            )

            unit_categorie_causa_solucao_text_response = model.generate_content(unit_categorie_causa_solucao_text)

            unit_categorie_email_text = (
                "Abaixo está um texto que você mesmo me gerou. \n"
                f"me retorne apenas o texto relacionado ao email gerado.\n\n"
                f"{response_categorie}"
                "'"
            )

            unit_categorie_email_text_response = model.generate_content(unit_categorie_email_text)

            result.append({
                {
                    "analise": unit_categorie_analise_text_response,
                    "causa_solucao": unit_categorie_causa_solucao_text_response,
                    "email_geral": unit_categorie_email_text_response,\
                }
            })
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise: {str(e)}")