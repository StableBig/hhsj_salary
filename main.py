import os
import time

import requests
from itertools import count
from dotenv import find_dotenv, load_dotenv
from terminaltables import AsciiTable


def calculate_avg_salary(salary_start, salary_end):
    """Calculate the average salary based on the given range."""
    if salary_start and salary_end:
        return (salary_start + salary_end) // 2
    elif salary_start and not salary_end:
        return int(salary_start * 1.2)
    elif not salary_start and salary_end:
        return int(salary_end * 0.8)
    else:
        return None

def fetch_hh_vacancies(program_language, moscow_id, amount_of_days, max_pages_hh, amount_of_vacancies_on_page, headers_hh):
    """Fetch job vacancies from HeadHunter API."""
    vacancies_hh = []
    for page in count(0):
        payload = {
            'area': moscow_id,
            'period': amount_of_days,
            'text': program_language,
            'per_page': amount_of_vacancies_on_page,
            'page': page
        }
        url_hh = 'https://api.hh.ru/vacancies'
        response = requests.get(url_hh, headers=headers_hh, params=payload)
        response.raise_for_status()
        vacancies_hh.append(response.json())
        if page >= max_pages_hh:
            break
        time.sleep(2)
    return vacancies_hh

def fetch_sj_vacancies(program_language, max_number_of_results, max_pages_sj, headers_sj):
    """Fetch job vacancies from SuperJob API."""
    vacancies_sj = []
    for page in count(0):
        payload_sj = {
            'town': 'Москва',
            'count': max_number_of_results,
            'period': 0,
            'keyword': program_language,
            'page': page
        }
        url_sj = 'https://api.superjob.ru/2.0/vacancies'
        response_sj = requests.get(url_sj, headers=headers_sj, params=payload_sj)
        response_sj.raise_for_status()
        vacancies_sj.append(response_sj.json())
        if page >= max_pages_sj:
            break
    return vacancies_sj

def process_hh_vacancies(vacancies_hh, estimate_salary_hh):
    """Process HeadHunter vacancies and calculate average salary."""
    salaries_hh = []
    for page_with_hh_vacancies in vacancies_hh:
        vacancies_items = page_with_hh_vacancies['items']
        for vacancy_hh in vacancies_items:
            if vacancy_hh['salary']:
                salaries_hh.append(estimate_salary_hh(vacancy_hh))
    return salaries_hh

def process_sj_vacancies(vacancies_sj, estimate_salary_sj):
    """Process SuperJob vacancies and calculate average salary."""
    salaries_sj = []
    for page_with_sj_vacancies in vacancies_sj:
        vacancies_sj_objects = page_with_sj_vacancies['objects']
        for vacancy_sj in vacancies_sj_objects:
            if vacancy_sj['payment_from'] != 0 or vacancy_sj['payment_to'] != 0:
                salaries_sj.append(estimate_salary_sj(vacancy_sj))
    return salaries_sj

def main():
    load_dotenv(find_dotenv())
    sj_key = os.environ.get('SUPERJOB_KEY')
    popular_languages = ['C', 'C++', 'C#', 'Java', 'JavaScript', 'Python', 'Ruby', 'Rust']
    moscow_id = 1
    amount_of_days = 31
    max_pages_hh = 20
    amount_of_vacancies_on_page = 50
    max_number_of_results = 100
    max_pages_sj = 5
    headers_hh = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    headers_sj = {
        'X-Api-App-Id': sj_key,
    }

    vacancies_language_hh = {}
    vacancies_language_sj = {}

    for program_language in popular_languages:
        vacancies_hh = fetch_hh_vacancies(program_language, moscow_id, amount_of_days, max_pages_hh, amount_of_vacancies_on_page, headers_hh)
        salaries_hh = process_hh_vacancies(vacancies_hh, estimate_salary_hh)
        average_hh_salary = sum(salaries_hh) // len(salaries_hh) if salaries_hh else 0
        vacancies_language_hh[program_language] = {
            'vacancies_found': len(vacancies_hh),
            'vacancies_processed': len(salaries_hh),
            'average_salary': average_hh_salary
        }

        vacancies_sj = fetch_sj_vacancies(program_language, max_number_of_results, max_pages_sj, headers_sj)
        salaries_sj = process_sj_vacancies(vacancies_sj, estimate_salary_sj)
        average_sj_salary = sum(salaries_sj) // len(salaries_sj) if salaries_sj else 0
        vacancies_language_sj[program_language] = {
            'vacancies_found': len(vacancies_sj),
            'vacancies_processed': len(salaries_sj),
            'average_salary': average_sj_salary
        }

    title_hh = 'HEADHUNTER (Moscow)'
    title_sj = 'SUPERJOB (Moscow)'

    print(create_table(vacancies_language_hh, title_hh))
    print(create_table(vacancies_language_sj, title_sj))

if __name__ == '__main__':
    main()
