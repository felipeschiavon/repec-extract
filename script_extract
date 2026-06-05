import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
import re

# ==============================================================================
# CONFIGURAÇÕES DA PESQUISA
# ==============================================================================
# Insira aqui a sua query
query = """("female economic empowerment" | "women's economic empowerment" | "women economic empowerment" | "economic empowerment" | "economic autonomy" | "financial autonomy" | "financial independence" | "financial inclusion" | "income generation" | employment | "women's employment" | "female employment" | "paid work" | "labor force participation" | "labour force participation" | entrepreneurship | microfinance | microcredit | "cash transfer" | "cash transfers" | "conditional cash transfer" | "conditional cash transfers" | "cash transfer program" | "cash transfer programme" | savings | "access to assets" | "control over resources" | "economic decision-making") + ("violence against women" | "intimate partner violence" | IPV | "domestic violence" | "domestic abuse" | "gender-based violence" | "physical violence" | "sexual violence" | "psychological violence" | "emotional violence" | "economic violence" | "economic abuse" | "financial abuse" | "coercive control" | "controlling behavior" | "controlling behaviours" | "femicide" | "feminicide")"""

# ==============================================================================
# SCRIPT DE EXTRAÇÃO
# ==============================================================================
query_encoded = urllib.parse.quote_plus(query)
base_url = f"https://ideas.repec.org/cgi-bin/htsearch?q={query_encoded}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

artigos = []
pagina_atual = 1
url_atual = base_url

print("Iniciando a extração do IDEAS RePEc...")

while url_atual:
    print(f"Raspando página {pagina_atual}...")
    response = requests.get(url_atual, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro ao acessar a página. Código: {response.status_code}")
        break
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # O IDEAS geralmente retorna os itens em uma lista ordenada <ol>
    lista_resultados = soup.find('ol')
    
    if not lista_resultados:
        print("Nenhum resultado encontrado nesta página (ou estrutura mudou).")
        break
        
    itens = lista_resultados.find_all('li')
    
    for item in itens:
        texto_item = item.text.strip()
        
        # O Handle fica sempre no final com o prefixo RePEc:
        match_handle = re.search(r"RePEc:[\w\-:]+", texto_item)
        handle = match_handle.group(0) if match_handle else "Não encontrado"
        
        # Pega a primeira tag <a> que costuma ter o título
        titulo_tag = item.find('a')
        titulo = titulo_tag.text.strip() if titulo_tag else "Sem Título"
        
        # Pega o link do artigo
        link = "https://ideas.repec.org" + titulo_tag['href'] if titulo_tag and titulo_tag.has_attr('href') else ""
        
        # Adiciona na lista geral
        artigos.append({
            "Título_Completo_Texto": texto_item.replace("\n", " ")[:150] + "...", # Uma prévia do texto
            "Título_Extraído": titulo,
            "URL": link,
            "Handle": handle
        })
    
    # Procurar o link da Próxima Página
    # A estrutura típica é um link com o texto "Next" ou imagem
    proxima_pag_tag = soup.find('a', string=re.compile("Next", re.IGNORECASE))
    
    if proxima_pag_tag and proxima_pag_tag.has_attr('href'):
        url_atual = "https://ideas.repec.org" + proxima_pag_tag['href']
        pagina_atual += 1
        time.sleep(3) # Pausa amigável para não ser bloqueado
    else:
        url_atual = None

# ==============================================================================
# SALVANDO OS RESULTADOS
# ==============================================================================
print(f"\nConcluído! {len(artigos)} registros extraídos.")

if artigos:
    df = pd.DataFrame(artigos)
    
    # OPÇÃO 1: Salva TUDO em um Excel
    df.to_excel("Dados_Completos_RePEc.xlsx", index=False)
    print("-> Arquivo 'Dados_Completos_RePEc.xlsx' gerado com sucesso!")
    
    # OPÇÃO 2: Salva apenas os Handles em um arquivo TXT/CSV limpo
    handles_limpos = df[df['Handle'] != "Não encontrado"]['Handle'].unique()
    pd.DataFrame(handles_limpos, columns=['Handle']).to_csv("Lista_Handles_RePEc.csv", index=False)
    print("-> Arquivo 'Lista_Handles_RePEc.csv' gerado com sucesso!")
