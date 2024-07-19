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

def scrape_catho():
    base_urls = [
        'https://www.catho.com.br/vagas/',
        'https://www.catho.com.br/vagas/estagio/',
        'https://www.catho.com.br/vagas/estagiario/'
    ]
    
    keywords = [
        'excel'
    ]
    
    city_query = '?cidade_id[0]=776&cidade_id[1]=392&cidade_id[2]=839&cidade_id[3]=143'
    date_query = '&lastDays=30'
    area_queries = {
        'Administração': '&area_id[0]=1&area_id[1]=3&area_id[2]=12&area_id[3]=20&area_id[4]=47&area_id[5]=67&area_id[6]=69&area_id[7]=73&area_id[8]=74&area_id[9]=75&area_id[10]=1906&area_id[11]=1937',
        'Comercial e Vendas': '&area_id[0]=14',
        'Comércio Exterior': '&area_id[0]=15&area_id[1]=70'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    jobs = []
    processed_ids = set()
    
    for base_url in base_urls:
        for keyword in keywords:
            for area_name, area_query in area_queries.items():
                if 'estagio' in base_url:
                    url = f"{base_url.replace('/estagio/', '/estagio-')}{keyword}/{city_query}{area_query}{date_query}"
                elif 'estagiario' in base_url:
                    url = f"{base_url.replace('/estagiario/', '/estagiario-')}{keyword}/{city_query}{area_query}{date_query}"
                else:
                    url = f"{base_url}{keyword}/{city_query}{area_query}{date_query}"
                
                time.sleep(random.uniform(2, 3))
                
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
                        
                        tipo_vaga = 'Estágio' if 'estagio' in base_url or 'estagiario' in base_url else job_data.get('regimeContrato', 'N/A')
                        
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
                        
                        if any(field in [id_vaga, nome_vaga, localizacao, tipo_vaga, area, empresa, descricao, create_at] for field in ['N/A', '']):
                            continue
                        
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
    
    return jobs
