import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

def get_job_description(job_url):
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
                
            return description
    
    return "Description not available"

def get_site_name(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    parts = domain.split('.')
    if len(parts) > 2:
        return parts[-2]
    return parts[0]

url = 'https://www.linkedin.com/jobs/search?keywords=Tecnologia%20Da%20Informação&location=São%20José%20dos%20Campos%2C%20São%20Paulo%2C%20Brasil&pageNum=0'
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    job_listings = soup.find_all('div', {'class':'job-search-card'})
    
    job_data = []
    
    count = 0
    for job in job_listings:
        if count >= 10:
            break
        
        title = job.find('h3', {'class': 'base-search-card__title'}).text.strip()
        company = job.find('a', {'class': 'hidden-nested-link'}).text.strip()
        location = job.find('span', {'class': 'job-search-card__location'}).text.strip()
        
        if "São José dos Campos" not in location:
            continue
        
        anchor_tag = job.find('a', class_='base-card__full-link')
        href_link = anchor_tag['href']
        description = get_job_description(href_link)
        site_name = get_site_name(href_link)
        
        time_tag_new = job.find('time', {'class': 'job-search-card__listdate--new'})
        time_tag = job.find('time', {'class': 'job-search-card__listdate'})
        posted_time = (time_tag_new.text.strip() if time_tag_new else time_tag.text.strip() if time_tag else "Not available")
        
        job_dict = {
            "id_vaga": 'N/A',
            "local_dado": site_name,
            "nome_vaga": title,
            "localizacao": location,
            "tipo_vaga": 'N/A',
            "area": "N/A",
            "empresa": company,
            "descricao": description,
            "link": href_link,
            "create_at": posted_time,
            "update_at": posted_time
        }
        
        job_data.append(job_dict)
        
        count += 1
    
    print(json.dumps(job_data, indent=2, ensure_ascii=False))
else:
    print("Failed to fetch job listings.")
