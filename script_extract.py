import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# URL do script que processa o formulário via POST
url_busca = "https://ideas.repec.org/cgi-bin/htsearch2"

# Sua query booleana estruturada
query = """("female economic empowerment" | "women's economic empowerment" | "women economic empowerment" | "economic empowerment" | "economic autonomy" | "financial autonomy" | "financial independence" | "financial inclusion" | "income generation" | employment | "women's employment" | "female employment" | "paid work" | "labor force participation" | "labour force participation" | entrepreneurship | microfinance | microcredit | "cash transfer" | "cash transfers" | "conditional cash transfer" | "conditional cash transfers" | "cash transfer program" | "cash transfer programme" | savings | "access to assets" | "control over resources" | "economic decision-making") + ("violence against women" | "intimate partner violence" | IPV | "domestic violence" | "domestic abuse" | "gender-based violence" | "physical violence" | "sexual violence" | "psychological violence" | "emotional violence" | "economic violence" | "economic abuse" | "financial abuse" | "coercive control" | "controlling behavior" | "controlling behaviours" | "femicide" | "feminicide")"""

# Dados do formulário (Payload do POST) mapeados do sistema htsearch2
form_data = {
    "q": query,
    "ul": "",         # Todo o site
    "wf": "5B11",     # Busca booleana avançada
    "s": "Y",         # Ordenar por ano
    "b": "2015",      # Ano inicial
    "e": "2026",      # Ano final
    "start": 1        # Ponteiro do resultado inicial (Página 1 = 1, Página 2 = 11...)
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://ideas.repec.org',
    'Referer': 'https://ideas.repec.org/search.html'
}

artigos = []
pagina_atual = 1
max_paginas = 60 # Margem de segurança para cobrir os 577 artigos (10 por página)

print("Iniciando a extração via requisições POST automatizadas...")

for p in range(max_paginas):
    print(f"Processando página {pagina_atual} (Resultados começando em: {form_data['start']})...")
    
    # Enviando como POST (data=form_data) simulando o clique do botão de busca
    response = requests.post(url_busca, data=form_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro no servidor do RePEc. Status: {response.status_code}")
        break
        
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text()
    
    # Coleta todos os Handles da página usando Expressão Regular
    handles_na_pagina = re.findall(r"RePEc:[\w\-:]+", text_content)
    
    if not handles_na_pagina:
        print("Nenhum Handle RePEc localizado nesta página. Chegamos ao fim dos resultados.")
        break
        
    # Extração estruturada baseada na lista <ol> do site
    lista_resultados = soup.find('ol')
    novos_adicionados = 0
    
    if lista_resultados:
        itens = lista_resultados.find_all('li')
        for item in itens:
            texto_item = item.text.strip()
            match_handle = re.search(r"RePEc:[\w\-:]+", texto_item)
            handle = match_handle.group(0) if match_handle else "Não encontrado"
            
            titulo_tag = item.find('a')
            titulo = titulo_tag.text.strip() if titulo_tag else "Sem Título"
            link = "https://ideas.repec.org" + titulo_tag['href'] if titulo_tag and titulo_tag.has_attr('href') else ""
            
            if handle != "Não encontrado":
                artigos.append({
                    "Título": titulo,
                    "URL": link,
                    "Handle": handle,
                    "Resumo_Bruto": texto_item.replace("\n", " ")
                })
                novos_adicionados += 1
    else:
        # Fallback via Regex pura caso falte a tag <ol>
        for h in set(handles_na_pagina):
            artigos.append({
                "Título": "Coletado via Expressão Regular",
                "URL": "",
                "Handle": h,
                "Resumo_Bruto": ""
            })
            novos_adicionados += 1

    print(f"-> {novos_adicionados} registros identificados na página {pagina_atual}.")
    
    # O motor deles avança de 10 em 10 itens por página
    form_data['start'] += 10
    pagina_atual += 1
    
    # Delay de segurança obrigatório para evitar bloqueios de IP
    time.sleep(3.0)

# ==============================================================================
# GERAÇÃO DOS ARQUIVOS (OPÇÃO 1 E OPÇÃO 2)
# ==============================================================================
print(f"\nVarredura concluída. Total geral capturado: {len(artigos)}")

if artigos:
    df = pd.DataFrame(artigos)
    
    # Limpa duplicados potenciais
    df = df.drop_duplicates(subset=['Handle'])
    print(f"Total líquido de artigos salvos: {len(df)}")
    
    # Opção 1: Excel completo
    df.to_excel("Dados_Completos_RePEc.xlsx", index=False)
    print("-> Sucesso: 'Dados_Completos_RePEc.xlsx' salvo.")
    
    # Opção 2: CSV limpo de Handles para a API
    df_handles = df[['Handle']]
    df_handles.to_csv("Lista_Handles_RePEc.csv", index=False)
    print("-> Sucesso: 'Lista_Handles_RePEc.csv' salvo.")
else:
    print("Nenhum dado foi estruturado. Verifique a conexão ou os parâmetros.")
