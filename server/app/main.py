"""Servidor da API de avaliações da loja (FastAPI).

Rodar a partir da raiz do projeto:
    uvicorn server.app.main:app --reload
Documentação automática: http://127.0.0.1:8000/docs
"""
import os
from collections import Counter
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from .sentimento import analisar_texto

LOJA = os.getenv("LOJA_NOME", "Loja do NARGAS")

app = FastAPI(
    title=f"Avaliações – {LOJA}",
    description="Recebe avaliações de clientes da loja e classifica cada uma em positivo, neutro ou negativo.",
    version="1.0.0",
)

# Se API_KEY estiver definida no ambiente, as rotas exigem o header X-API-Key.
API_KEY = os.getenv("API_KEY", "")

# "Banco de dados" em memória (some quando o servidor reinicia).
historico = []
proximo_id = 1


def verificar_chave(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Chave de API inválida ou ausente.")


class TextoEntrada(BaseModel):
    texto: str = Field(..., min_length=3, max_length=1000, examples=["Adorei o atendimento, recomendo!"])
    autor: str = Field(default="Anônimo", max_length=50, examples=["Maria"])


class Resultado(BaseModel):
    id: int
    autor: str
    texto: str
    sentimento: str
    pontuacao: int
    confianca: float
    palavras_chave: list
    data_hora: str


@app.get("/")
def raiz():
    return {"mensagem": f"API de avaliações da {LOJA} no ar.", "docs": "/docs"}


@app.post("/analisar", response_model=Resultado, status_code=201, dependencies=[Depends(verificar_chave)])
def analisar(entrada: TextoEntrada):
    global proximo_id
    resultado = analisar_texto(entrada.texto)
    registro = {
        "id": proximo_id,
        "autor": entrada.autor,
        "texto": entrada.texto,
        "data_hora": datetime.now().isoformat(timespec="seconds"),
        **resultado,
    }
    proximo_id += 1
    historico.append(registro)
    return registro


@app.get("/historico", response_model=list[Resultado], dependencies=[Depends(verificar_chave)])
def listar_historico(
    sentimento: Optional[str] = Query(default=None, description="positivo, negativo ou neutro"),
    limite: int = Query(default=20, ge=1, le=100),
):
    itens = historico
    if sentimento:
        itens = [r for r in itens if r["sentimento"] == sentimento.lower()]
    return itens[-limite:]


@app.get("/historico/{id_analise}", response_model=Resultado, dependencies=[Depends(verificar_chave)])
def buscar_analise(id_analise: int):
    for registro in historico:
        if registro["id"] == id_analise:
            return registro
    raise HTTPException(status_code=404, detail="Análise não encontrada.")


@app.get("/estatisticas", dependencies=[Depends(verificar_chave)])
def estatisticas():
    total = len(historico)
    contagem = Counter(r["sentimento"] for r in historico)

    def pct(chave):
        return round(100 * contagem.get(chave, 0) / total, 1) if total else 0.0

    return {
        "loja": LOJA,
        "total": total,
        "positivo": contagem.get("positivo", 0),
        "neutro": contagem.get("neutro", 0),
        "negativo": contagem.get("negativo", 0),
        "percentual_positivo": pct("positivo"),
        "percentual_neutro": pct("neutro"),
        "percentual_negativo": pct("negativo"),
    }


@app.delete("/historico", dependencies=[Depends(verificar_chave)])
def limpar_historico():
    removidos = len(historico)
    historico.clear()
    return {"removidos": removidos}
