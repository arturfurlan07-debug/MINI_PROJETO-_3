"""Cliente que consome a API de avaliações da loja (análise de sentimento).

Rodar (com o servidor no ar):
    python client/main.py
Variáveis de ambiente (opcionais):
    API_URL  endereço do servidor (padrão: http://127.0.0.1:8000)
    API_KEY  chave enviada no header X-API-Key (só se o servidor exigir)
"""
import os

import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}
TIMEOUT = 10


def chamar(metodo, caminho, **kwargs):
    """Faz a requisição e trata os erros mais comuns."""
    try:
        resposta = requests.request(metodo, f"{API_URL}{caminho}", headers=HEADERS,
                                    timeout=TIMEOUT, **kwargs)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.ConnectionError:
        print(f"Não consegui conectar em {API_URL}. O servidor está no ar?")
    except requests.exceptions.HTTPError as erro:
        print(f"Erro da API ({erro.response.status_code}): {erro.response.text}")
    except requests.exceptions.Timeout:
        print("A API demorou demais para responder.")
    return None


def analisar(texto, autor="Anônimo"):
    return chamar("POST", "/analisar", json={"texto": texto, "autor": autor})


def historico(sentimento=None, limite=20):
    params = {"limite": limite}
    if sentimento:
        params["sentimento"] = sentimento
    return chamar("GET", "/historico", params=params)


def estatisticas():
    return chamar("GET", "/estatisticas")


def limpar():
    return chamar("DELETE", "/historico")


def mostrar_resultado(r):
    print(f"#{r['id']} {r['autor']} - [{r['sentimento'].upper()}] confiança {r['confianca']:.0%} "
          f"| palavras: {', '.join(r['palavras_chave']) or '-'}")
    print(f"     \"{r['texto']}\"")


def mostrar_painel():
    """Painel de avaliações da loja: quantidade e barra de cada sentimento."""
    est = estatisticas()
    if not est:
        return
    print(f"\n===== AVALIAÇÕES - {est['loja']} ({est['total']} no total) =====")
    for nome, chave in (("Positivas", "positivo"), ("Neutras", "neutro"), ("Negativas", "negativo")):
        pct = est[f"percentual_{chave}"]
        barra = "█" * round(pct / 5)
        print(f"{nome:<10} {barra:<20} {pct:>5}% ({est[chave]})")


def demo():
    """Envia avaliações de exemplo de clientes e mostra o painel da loja."""
    avaliacoes = [
        ("Maria", "Adorei o atendimento, produto de ótima qualidade. Recomendo!"),
        ("João", "Péssimo, chegou quebrado e a entrega foi muito demorada."),
        ("Ana", "Não gostei da embalagem, mas o produto é bom."),
        ("Pedro", "Chegou na terça-feira."),
        ("Carla", "Entrega rápida e preço barato, super satisfeito!"),
        ("Lucas", "Horrível, não recomendo. Tive problemas com o suporte."),
    ]
    print("== Enviando avaliações dos clientes ==")
    for autor, texto in avaliacoes:
        resultado = analisar(texto, autor)
        if resultado is None:
            return
        mostrar_resultado(resultado)

    mostrar_painel()

    print("\n== Avaliações negativas ==")
    for r in historico(sentimento="negativo") or []:
        mostrar_resultado(r)


MENU = """
===== AVALIAÇÕES DA LOJA =====
1 Enviar uma avaliação
2 Ver avaliações
3 Ver painel (positivas/neutras/negativas)
4 Limpar avaliações
5 Rodar demonstração
0 Sair"""


def menu():
    while True:
        print(MENU)
        op = input("Opção: ").strip()
        if op == "0":
            break
        elif op == "1":
            autor = input("Seu nome (Enter = anônimo): ").strip() or "Anônimo"
            r = analisar(input("Sua avaliação: ").strip(), autor)
            if r:
                mostrar_resultado(r)
        elif op == "2":
            filtro = input("Filtrar (positivo/negativo/neutro, Enter = todos): ").strip() or None
            for r in historico(filtro) or []:
                mostrar_resultado(r)
        elif op == "3":
            mostrar_painel()
        elif op == "4":
            print(limpar())
        elif op == "5":
            demo()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
