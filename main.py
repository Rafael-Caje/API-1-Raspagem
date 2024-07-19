import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from modules.scrap_cath import scrape_catho
from modules.scrap_link import scrape_linkedin
from database.database import insert_job_data

def main():
    linkedin_jobs = scrape_linkedin()
    catho_jobs = scrape_catho()
    all_jobs = catho_jobs + linkedin_jobs
    response = insert_job_data(all_jobs)
    print(response)

if __name__ == '__main__':
    main()
    