# API de Avaliações da Loja do NARGAS

Terceiro Mini Projeto (**Consumo de APIs**) – Tecnologia em Inteligência Artificial, Fatec Rio Claro.

Servidor de API feito com **FastAPI** que recebe avaliações de clientes de uma loja e classifica cada uma em **positiva**, **neutra** ou **negativa** (análise de sentimento). As avaliações ficam guardadas em memória e a API monta um painel com a porcentagem de cada tipo, como nas telas de avaliação de lojas online.

Um **cliente** em Python (biblioteca `requests`) consome a API: envia avaliações, lista o histórico e mostra o painel no terminal.

## Tecnologias

- Python 3
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) (servidor)
- [Requests](https://requests.readthedocs.io/) (cliente)

## Estrutura do projeto

```
meu_projeto_api/
├── README.md
├── requirements.txt          # dependências Python
│
├── server/                   # Servidor da API (backend)
│   └── app/
│       ├── __init__.py
│       ├── main.py           # rotas da API (FastAPI)
│       └── sentimento.py     # lógica de análise de sentimento
│
└── client/                   # Cliente que consome a API
    └── main.py               # menu interativo e demonstração
```

## Como executar

### Pelo terminal

```bash
# 1) instalar as dependências
pip install -r requirements.txt

# 2) subir o servidor (na raiz do projeto)
uvicorn server.app.main:app --reload

# 3) em outro terminal, rodar o cliente
python client/main.py
```

O servidor fica em `http://127.0.0.1:8000`. A documentação interativa (Swagger) é gerada automaticamente em `http://127.0.0.1:8000/docs`.

### Pelo Google Colab

O notebook do repositório cria os arquivos, sobe o servidor em segundo plano dentro do próprio Colab e o cliente chama `http://127.0.0.1:8000`. Basta executar as células na ordem.

## Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Verifica se a API está no ar |
| POST | `/analisar` | Envia uma avaliação e recebe a classificação |
| GET | `/historico` | Lista as avaliações (`?sentimento=negativo&limite=10`) |
| GET | `/historico/{id}` | Busca uma avaliação pelo id |
| GET | `/estatisticas` | Painel da loja: totais e porcentagem de cada sentimento |
| DELETE | `/historico` | Apaga todas as avaliações |

### Exemplo de uso

Requisição:

```bash
curl -X POST http://127.0.0.1:8000/analisar \
  -H "Content-Type: application/json" \
  -d '{"autor": "Maria", "texto": "Adorei o atendimento, recomendo!"}'
```

Resposta (`201 Created`):

```json
{
  "id": 1,
  "autor": "Maria",
  "texto": "Adorei o atendimento, recomendo!",
  "sentimento": "positivo",
  "pontuacao": 2,
  "confianca": 1.0,
  "palavras_chave": ["adorei", "recomendo"],
  "data_hora": "2026-11-11T18:00:00"
}
```

Painel (`GET /estatisticas`):

```json
{
  "loja": "Loja do NARGAS",
  "total": 6,
  "positivo": 2,
  "neutro": 2,
  "negativo": 2,
  "percentual_positivo": 33.3,
  "percentual_neutro": 33.3,
  "percentual_negativo": 33.3
}
```

No terminal, o cliente mostra o painel assim:

```
===== AVALIAÇÕES - Loja do NARGAS (6 no total) =====
Positivas  ███████               33.3% (2)
Neutras    ███████               33.3% (2)
Negativas  ███████               33.3% (2)
```

## Como a análise de sentimento funciona

A classificação usa um **léxico** (lista de palavras positivas e negativas em português), sem bibliotecas externas:

1. O texto é colocado em minúsculas e sem acentos.
2. Cada palavra positiva soma +1 e cada negativa soma −1.
3. Uma negação até duas palavras antes inverte o sinal (por exemplo, "não gostei" e "não é bom" contam como negativo). A busca para se houver outra palavra de sentimento no meio.
4. Pontuação final maior que 0 é **positivo**, menor que 0 é **negativo** e igual a 0 é **neutro**.

Toda essa lógica está isolada em `server/app/sentimento.py`, então é possível trocá-la por um modelo de IA (como um modelo de `transformers`) sem alterar as rotas.

## Variáveis de ambiente (opcionais)

O código lê estas variáveis direto do ambiente. Todas são opcionais e têm valor padrão, então só defina se quiser mudar. Exemplo:

```bash
export LOJA_NOME="Loja do NARGAS"
export API_KEY="minha-chave"
```

| Variável | Onde | Para que serve |
|----------|------|----------------|
| `LOJA_NOME` | servidor | Nome da loja exibido na API e no painel |
| `API_KEY` | servidor e cliente | Se definida no servidor, as rotas exigem o header `X-API-Key` com o mesmo valor |
| `API_URL` | cliente | Endereço do servidor (padrão: `http://127.0.0.1:8000`) |


## Autores

- Artur Nagasima Furlan
- Vinicius Mends
