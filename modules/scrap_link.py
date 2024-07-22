from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dateutil.relativedelta import relativedelta
import re
import time

def get_job_description_and_details(job_url):
    response = requests.get(job_url)
    if response.status_code == 200:
        job_soup = BeautifulSoup(response.text, 'html.parser')
        
        description_tag = job_soup.find('div', {'class': 'show-more-less-html__markup'})
        if not description_tag:
            description_tag = job_soup.find('div', {'class': 'description__text'})
        if not description_tag:
            description_tag = job_soup.find('div', {'class': 'description'})
        if not description_tag:
            description_tag = job_soup.find('section', {'role': 'description'})
        if not description_tag:
            description_tag = job_soup.find('section', {'class': 'show-more-less-html'})
        
        if description_tag:
            description = description_tag.get_text(separator=" ", strip=True)
            description_words = description.split()[:50]
            
            if len(description_words) < len(description.split()):
                description = ' '.join(description_words) + '...'
            else:
                description = ' '.join(description_words)
                
        else:
            description = "Description not available"
        
        job_criteria = job_soup.find_all('li', {'class': 'description__job-criteria-item'})
        area = "N/A"
        tipo_vaga = "N/A"
        
        for criteria in job_criteria:
            subheader = criteria.find('h3', {'class': 'description__job-criteria-subheader'}).text.strip()
            criteria_text = criteria.find('span', {'class': 'description__job-criteria-text'}).text.strip()
            
            if subheader == "Setores":
                area = criteria_text
            elif subheader == "Tipo de emprego":
                tipo_vaga = criteria_text
        
        return description, area, tipo_vaga
    
    return "Description not available", "N/A", "N/A"

def get_site_name(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    parts = domain.split('.')
    if len(parts) > 2:
        return parts[-2]
    return parts[0]

def get_job_id_from_url(url):
    match = re.search(r'-(\d+)\?position', url)
    if match:
        return match.group(1)
    return None

def get_posted_time(relative_time_str):
    now = datetime.now(pytz.timezone('America/Sao_Paulo')).replace(hour=0, minute=0, second=0, microsecond=0)
    
    if "year" in relative_time_str:
        num_years = int(relative_time_str.split()[0])
        date = now - relativedelta(years=num_years)
    elif "month" in relative_time_str:
        num_months = int(relative_time_str.split()[0])
        date = now - relativedelta(months=num_months)
    elif "week" in relative_time_str:
        num_weeks = int(relative_time_str.split()[0])
        date = now - relativedelta(weeks=num_weeks)
    elif "day" in relative_time_str:
        num_days = int(relative_time_str.split()[0])
        date = now - relativedelta(days=num_days)
    elif "hour" in relative_time_str or "minute" in relative_time_str:
        date = now
    else:
        return None
    
    return date.strftime("%Y-%m-%d")

def scrape_linkedin():
    cities = [
        ("São José dos Campos", "São%20José%20dos%20Campos%2C%20São%20Paulo%2C%20Brasil"),
        ("Taubaté", "Taubaté%2C%20São%20Paulo%2C%20Brasil"),
        ("Caçapava", "Caçapava%2C%20São%20Paulo%2C%20Brasil"),
        ("Jacareí", "Jacareí%2C%20São%20Paulo%2C%20Brasil")
    ]
    
    job_titles = [
        "Desenvolvedor",
        "Estágio%2Bcomputação"
    ]
    
    job_data = []

    for city_name, city_url in cities:
        for job_title in job_titles:
            url = f'https://www.linkedin.com/jobs/search?keywords={job_title}&location={city_url}&pageNum=0'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_listings = soup.find_all('div', {'class':'job-search-card'})
                
                seen_ids = set()
                
                count = 0
                current_job_data = []
                for job in job_listings:
                    if count >= 5:  
                        break
                    
                    title = job.find('h3', {'class': 'base-search-card__title'}).text.strip()
                    company = job.find('a', {'class': 'hidden-nested-link'}).text.strip()
                    location = job.find('span', {'class': 'job-search-card__location'}).text.strip()
                    
                    if not any(city_part in location for city_part in ["São José dos Campos", "Taubaté", "Caçapava", "Jacareí"]):
                        continue
                    
                    anchor_tag = job.find('a', class_='base-card__full-link')
                    href_link = anchor_tag['href']
                    description, area, tipo_vaga = get_job_description_and_details(href_link)
                    id_vaga = get_job_id_from_url(href_link)

                    if id_vaga is None or id_vaga in seen_ids:
                        continue

                    time_tag_new = job.find('time', {'class': 'job-search-card__listdate--new'})
                    time_tag = job.find('time', {'class': 'job-search-card__listdate'})
                    relative_time = time_tag_new.text.strip() if time_tag_new else time_tag.text.strip() if time_tag else "Not available"

                    posted_time = get_posted_time(relative_time)

                    timezone_br = pytz.timezone('America/Sao_Paulo')
                    update_at = datetime.now(timezone_br).strftime("%Y-%m-%d")
                    
                    job_dict = {
                        "id_vaga": id_vaga,
                        "local_dado": 'LinkedIn',
                        "nome_vaga": title,
                        "localizacao": location,
                        "tipo_vaga": tipo_vaga,
                        "area": area,
                        "empresa": company,
                        "descricao": description,
                        "link": href_link,
                        "create_at": posted_time,
                        "update_at": update_at
                    }
                    
                    current_job_data.append(job_dict)
                    seen_ids.add(id_vaga)
                    
                    count += 1
                    
                    time.sleep(60)
                
                job_data.extend(current_job_data)
            time.sleep(60)

    limited_link = job_data[:10]
    return limited_link