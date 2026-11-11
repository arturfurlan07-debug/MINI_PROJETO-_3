"""Análise de sentimento simples (baseada em léxico) para textos em português.

Não usa bibliotecas externas: assim o servidor sobe rápido e o código é fácil
de explicar. Para evoluir, dá para trocar `analisar_texto` por um modelo de IA
(ex.: transformers) sem mudar o resto da API.
"""
import re
import unicodedata

POSITIVAS = {
    "bom", "boa", "otimo", "otima", "excelente", "maravilhoso", "maravilhosa",
    "adorei", "amei", "gostei", "recomendo", "perfeito", "perfeita", "rapido",
    "rapida", "eficiente", "legal", "incrivel", "satisfeito", "satisfeita",
    "feliz", "agradavel", "barato", "qualidade", "top", "show", "nota10",
    "atencioso", "atenciosa", "confiavel", "facil", "lindo", "linda",
}

NEGATIVAS = {
    "ruim", "pessimo", "pessima", "horrivel", "terrivel", "odiei", "detestei",
    "lento", "lenta", "demorado", "demorada", "caro", "cara", "defeito",
    "quebrado", "quebrada", "decepcionado", "decepcionada", "decepcionante",
    "problema", "problemas", "fraco", "fraca", "falso", "falsa", "golpe",
    "lixo", "insatisfeito", "insatisfeita", "arrependido", "arrependida",
    "dificil", "sujo", "suja", "grosso", "grossa", "enganoso", "enganosa",
}

NEGACOES = {"nao", "nunca", "jamais", "nem", "sem"}


def normalizar(texto: str) -> str:
    """Minúsculas e sem acentos: 'Ótimo' vira 'otimo'."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def tokenizar(texto: str) -> list:
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def analisar_texto(texto: str) -> dict:
    """Devolve {'sentimento', 'pontuacao', 'confianca', 'palavras_chave'}.

    Uma negação logo antes da palavra inverte o sinal ("não gostei" -> negativo).
    """
    palavras = tokenizar(texto)
    pontuacao = 0
    chaves = []
    for i, palavra in enumerate(palavras):
        if palavra in POSITIVAS:
            valor = 1
        elif palavra in NEGATIVAS:
            valor = -1
        else:
            continue
        if i > 0 and palavras[i - 1] in NEGACOES:
            valor = -valor
        pontuacao += valor
        chaves.append(palavra)

    if pontuacao > 0:
        sentimento = "positivo"
    elif pontuacao < 0:
        sentimento = "negativo"
    else:
        sentimento = "neutro"

    confianca = 0.5 if not chaves else min(1.0, 0.5 + abs(pontuacao) / (2 * len(chaves)))
    if sentimento == "neutro" and chaves:
        confianca = 0.5  # sinais opostos que se cancelam

    return {
        "sentimento": sentimento,
        "pontuacao": pontuacao,
        "confianca": round(confianca, 2),
        "palavras_chave": chaves,
    }
