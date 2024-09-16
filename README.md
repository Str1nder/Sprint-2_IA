CAIO VITOR URBANO NEVES RM552392
EMILE DE MOURA MAIA RM552235
GUILHERME PEREIRA DE OLIVEIRA RM552238
JULIA ANDRADE DIAS RM552332
MARIA EDUARDA COSTA DE ARAÚJO VIEIRA RM98760


# Insight IA

### Visão Geral
O projeto InsightIA foi desenvolvido para coletar, processar e analisar reclamações de empresas publicadas na plataforma ReclameAqui. Ele permite a extração de insights valiosos a partir de dados coletados automaticamente, oferecendo uma visão clara e detalhada do comportamento das empresas em relações as suas reclamação no mercado.

### Funcionalidades Implementadas
- Análise de Reclamações: Processamento e categorização das reclamações para gerar insights.
- Relatórios e Insights: Exibição dos resultados coletados e processados, permitindo análises detalhadas.

### Endpoints

#### 1. web Scraping

**`GET /scraping/{empresa}`**

Realiza o scraping das reclamações para uma empresa específica.

- **Parâmetros de Consulta**:
  - `uuid`: Identificador do usuário no Firestore.
  - `empresa`: Nome da empresa a ser pesquisada (espaços substituídos por hífens).
  - `apelido` (opcional): Apelido para o nome da empresa.
  - `max_page` (opcional): Número máximo de páginas para scraping.
 
**Exemplo de Request:**

```http
GET /scraping/exemplo-empresa?uuid=1234&apelido=Exemplo&max_page=5
```

**Resposta**
```
{
  "status_code": 200,
  "mensagem": "Dados coletados e salvos com sucesso",
  "dados": { ... }
}
```

#### 2. Consultar Reclamações

**`GET /reclamacoes/{empresa}`**

Consulta as reclamações armazenadas para uma empresa específica.

- Parâmentros de Consulta:
  - `empresa`: Nome da empresa (espaços substituídos por hífens).
  - `uuid`: Identificador do usuário no Firestore.

**Exemplo de Request**

```http
GET /reclamacoes/exemplo-empresa?uuid=1234
```

**Resposta**
```
{
  "status_code": 200,
  "dados": { ... }
}
```

#### 3. Apagar Reclamações

**`DELETE /reclamacoes/{empresa}`**

Remove todas as reclamações armazenadas para uma empresa específica.

- Parâmetros de Consulta:
  - `empresa`: Nome da empresa (espaços substituídos por hífens).
  - `uuid`: Identificador do usuário no Firestore.

**Exemplo de Request**

```http
DELETE /reclamacoes/exemplo-empresa?uuid=1234
```

**Resposta**

```
{
  "status_code": 200,
  "mensagem": "Reclamações para a empresa exemplo-empresa foram apagadas com sucesso."
}
```

#### 4. Gerar insight interno

**`POST /insight/interno`**

Gera uma análise interna sobre as reclamações para uma empresa específica.

- Corpo de Requisição:
  - `uuid`: Identificador do usuário no Firestore.
  - `empresa`: Nome da empresa (espaços substituídos por hífens).

**Exemplo de Request:**

```
{
  "uuid": "1234",
  "empresa": "exemplo-empresa"
}
```

**Resposta**

```
{
  "status_code": 200,
  "análise_por_categoria": { ... }
}
```

#### 5. Gerar insight concorrente

**`POST /insight/concorrente`**

Gera uma análise comparativa entre a empresa interna e uma empresa concorrente.

- Corpo da Requisição:
  - `uuid`: Identificador do usuário no Firestore.
  - `empresa_interna`: Nome da empresa interna (espaços substituídos por hífens).
  - `empresa_externa`: Nome da empresa concorrente (espaços substituídos por hífens).


**Exemplo de Request**

```
{
  "uuid": "1234",
  "empresa_interna": "exemplo-empresa-interna",
  "empresa_externa": "exemplo-empresa-externa"
}
```

**Resposta**

```
{
  "status_code": 200,
  "comparacao": { ... }
}
```

### Instalação

#### 1. Clone o repositório
```
git clone https://github.com/seuusuario/InsightIA_API.git
cd InsightIA_API
```

#### 2. Crie e ative um ambiente virtual
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

#### 3. Instale as dependências
```
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

```
FIREBASE_CREDENTIALS={ ... }
GEMINI_API_KEY={ ... }
```
Substitua { ... } pelos valores apropriados.

### Executar o servidor
```
uvicorn main:appApi --reload
```

### Considerações
- Variáveis de Ambiente: Assegure-se de que as variáveis de ambiente estejam configuradas corretamente no arquivo `.env`.
- Credenciais do Firebase: Certifique-se de que o Firebase Firestore está corretamente configurado e acessível.


##### Link para o backend completo do projeto
https://github.com/GitHubWithCjcnch/InsightIA_API/tree/caio

