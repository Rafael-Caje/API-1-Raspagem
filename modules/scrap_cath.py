import json
import pytz
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import unicodedata
import random

def normalize_text(text):
    normalized = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    normalized = normalized.lower().strip().replace(' ', '-')
    return normalized

def get_city_from_ids(city_list):
    city_priority = ['776', '392', '143', '839']
    for city_id in city_priority:
        for city in city_list:
            if str(city.get('cidadeId')) == city_id:
                return city.get('cidade')
    return 'Vale do Paraíba'


def generate_area_query(ids):
    return '&' + '&'.join(f'area_id[{i}]={id}' for i, id in enumerate(ids))

def scrape_catho():
    base_urls = [
        'https://www.catho.com.br/vagas/'
    ]
    
    keywords = ['desenvolvimento-de-software', 'analise-de-sistemas', 'programacao', 'arquitetura-de-software', 'sql',
                'big-data', 'gestao-de-producao', 'controle-de-qualidade', 'gestao-empresarial', 'planejamento-estrategico',
                'gestao-de-projetos', 'supply-chain-management', 'logistica-internacional', 'manufatura-inteligente', 'industria-4-0',
                'manutencao-aeronautica', 'engenharia-de-manutencao', 'aviacao-comercial', 'projetos-aeronauticos', 'analise-estrutural']
    
    city_query = '?cidade_id[0]=776&cidade_id[1]=392&cidade_id[2]=839&cidade_id[3]=143'
    date_query = '&lastDays=30'
    area_queries = {
        'Administração': generate_area_query([1, 3, 12, 20, 47, 67, 69, 73, 74, 75, 1906, 1937]),
        'Comercial e Vendas': generate_area_query([14]),
        'Comércio Exterior': generate_area_query([15, 70]),
        'Educação': generate_area_query([24, 87]),
        'Financeira': generate_area_query([2, 11, 19, 23, 40, 76]),
        'Hotelaria e Turismo': generate_area_query([48, 72]),
        'T.I': generate_area_query([51, 52]),
        'Saúde': generate_area_query([13, 26, 39, 41, 43, 45, 46, 58, 61, 62, 65, 1902]),
        'Suprimentos': generate_area_query([55, 88]),
        'Agricultura, Pecuária e Veterinária': generate_area_query([1858, 1859, 1904, 1943]),
        'Artes, Arquitetura e Design': generate_area_query([5, 6, 7, 21, 60]),
        'Comunicação / Marketing': generate_area_query([53, 57, 66, 71, 1965]),
        'Engenharia': generate_area_query([18, 29, 30, 31, 32, 34, 35, 36, 37, 38, 483, 484]),
        'Industrial': generate_area_query([9, 10, 25, 50, 56]),
        'Jurídica': generate_area_query([54]),
        'Técnica': generate_area_query([79, 80]),
        'Telemarketing': generate_area_query([8]),
        'Telecomunicações': generate_area_query([33]),
        'Serviços Sociais': generate_area_query([77])
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    jobs = []
    processed_ids = set()
    
    for base_url in base_urls:
        for keyword in keywords:
            for area_name, area_query in area_queries.items():
                url = f"{base_url}{keyword}/{city_query}{area_query}{date_query}"
                
                # time.sleep(random.uniform(0, 1))
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    print(f"Página carregada com sucesso! URL: {url}")
                else:
                    print(f"Erro ao carregar página. Status da requisição: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                script_tag = soup.find('script', type='application/json')
                
                if script_tag:
                    try:
                        json_data = json.loads(script_tag.string)
                        jobs_list = json_data['props']['pageProps']['jobSearch']['jobSearchResult']['data']['jobs']

                    except json.JSONDecodeError:
                        print(f"Erro ao decodificar JSON para o script: {script_tag.string}")
                        continue
                    
                    for job_json in jobs_list:
                        if not job_json.get('engaged_hirer', False):
                            continue
                        
                        job_data = job_json.get('job_customized_data', {})
                        
                        id_vaga = job_json.get('job_id', '')
                        
                        if id_vaga in processed_ids:
                            continue
                        
                        nome_vaga = job_data.get('titulo', 'N/A')
                        
                        cidade_info = job_data.get('vagas', [])
                        localizacao = get_city_from_ids(cidade_info)
                        
                        if localizacao == 'Vale do Paraíba':
                            continue
                        
                        tipo_vaga = 'Estágio' if 'estagi' in normalize_text(nome_vaga) else 'Contratos (CLT, PJ, outros)'
                        
                        area = ''
                        for area_key, area_query in area_queries.items():
                            if area_query in url:
                                area = area_key
                                break
                        if area == '':
                            continue
                        
                        empresa = job_data.get('contratante', {}).get('nome', 'N/A')
                        
                        descricao = job_data.get('descricao', 'N/A')
                        descricao = ' '.join(descricao.split()[:100]) + '...' if len(descricao.split()) > 100 else descricao
                        
                        link = f"https://www.catho.com.br/vagas/{normalize_text(nome_vaga)}/{id_vaga}/"
                        
                        data_atualizacao = job_data.get('dataAtualizacao', '')
                        if data_atualizacao:
                            try:
                                create_at = datetime.strptime(data_atualizacao, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                            except ValueError:
                                create_at = 'N/A'
                        else:
                            create_at = 'N/A'

                        timezone_br = pytz.timezone('America/Sao_Paulo')
                        update_at = datetime.now(timezone_br).strftime("%Y-%m-%d")
                        
                        # if any(field in [id_vaga, nome_vaga, localizacao, tipo_vaga, area, empresa, descricao, create_at] for field in ['N/A', '']):
                        #     continue
                        
                        jobs.append({
                            'id_vaga': id_vaga,
                            'local_dado': 'Catho',
                            'nome_vaga': nome_vaga,
                            'localizacao': localizacao,
                            'tipo_vaga': tipo_vaga,
                            'area': area,
                            'empresa': empresa,
                            'descricao': descricao,
                            'link': link,
                            'create_at': create_at,
                            'update_at': update_at
                        })
                        
                        processed_ids.add(id_vaga)
                        
    limited_cath = jobs[:10]
    return limited_cath

# if __name__ == "__main__":
#     jobs = scrape_catho()[:20]
#     print(f"Total de vagas encontradas: {len(jobs)}")
#     for job in jobs:
#         print(job)
