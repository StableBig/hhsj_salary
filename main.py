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


def estimate_salary_hh(vacancy_hh):
    """Estimate average salary from HeadHunter vacancy."""
    salary_from_hh = vacancy_hh['salary']['from']
    salary_to_hh = vacancy_hh['salary']['to']
    return calculate_avg_salary(salary_from_hh, salary_to_hh)


def estimate_salary_sj(vacancy_sj):
    """Estimate average salary from SuperJob vacancy."""
    salary_from_sj = vacancy_sj['payment_from']
    salary_to_sj = vacancy_sj['payment_to']
    return calculate_avg_salary(salary_from_sj, salary_to_sj)


def create_table(vacancies, title):
    """Build a table with given data and header."""
    vacancies_table = []
    table_headers = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]
    vacancies_table.append(table_headers)
    for language, vacancy_information in vacancies.items():
        vacancies_table.append(
            [
                language,
                vacancy_information.get('vacancies_found'),
                vacancy_information.get('vacancies_processed'),
                vacancy_information.get('average_salary'),
            ]
        )
    table = AsciiTable(vacancies_table)
    table.title = title
    return table.table


def get_hh_vacancies(program_language):
    """Retrieve HeadHunter vacancies for a programming language."""
    moscow_id = 1
    amount_of_days = 31
    max_pages_hh = 20
    amount_of_vacancies_on_page = 50
    headers_hh = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    vacancies_hh_found = 0
    average_hh_salary = 0
    vacancies_hh_processed = 0
    vacancies_hh = []
    salaries_hh = []
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
    vacancies_hh_found, vacancies_hh_processed, salaries_hh = process_hh_vacancies(vacancies_hh)
    return vacancies_hh_found, average_hh_salary, vacancies_hh_processed, vacancies_hh, salaries_hh


def process_hh_vacancies(vacancies_hh):
    """Process HeadHunter vacancies and calculate statistics."""
    vacancies_hh_found = 0
    salaries_hh = []
    for page_with_hh_vacancies in vacancies_hh:
        vacancies_items = page_with_hh_vacancies['items']
        vacancies_hh_found = page_with_hh_vacancies['found']
        for vacancy_hh in vacancies_items:
            if vacancy_hh['salary']:
                salaries_hh.append(estimate_salary_hh(vacancy_hh))
    vacancies_hh_processed = len(salaries_hh)
    return vacancies_hh_found, vacancies_hh_processed, salaries_hh


def get_sj_vacancies(program_language_sj):
    """Retrieve SuperJob vacancies for a programming language."""
    max_number_of_results = 100
    publication_period = 0
    max_pages_sj = 5
    headers_sj = {
        'X-Api-App-Id': os.environ.get('SUPERJOB_KEY'),
    }
    vacancies_sj_found = 0
    average_sj_salary = 0
    vacancies_sj_processed = 0
    vacancies_sj = []
    salaries_sj = []
    for page in count(0):
        payload_sj = {
            'town': 'Москва',
            'count': max_number_of_results,
            'period': publication_period,
            'keyword': program_language_sj,
            'page': page
        }
        url_sj = 'https://api.superjob.ru/2.0/vacancies'
        response_sj = requests.get(
            url_sj,
            headers=headers_sj,
            params=payload_sj
        )
        response_sj.raise_for_status()
        vacancies_sj.append(response_sj.json())
        if page >= max_pages_sj:
            break
    vacancies_sj_found, vacancies_sj_processed, salaries_sj = process_sj_vacancies(vacancies_sj)
    return vacancies_sj_found, average_sj_salary, vacancies_sj_processed, vacancies_sj, salaries_sj


def process_sj_vacancies(vacancies_sj):
    """Process SuperJob vacancies and calculate statistics."""
    vacancies_sj_found = 0
    salaries_sj = []
    for page_with_sj_vacancies in vacancies_sj:
        vacancies_sj_objects = page_with_sj_vacancies['objects']
        vacancies_sj_found = page_with_sj_vacancies['total']
        for vacancy_sj in vacancies_sj_objects:
            if vacancy_sj['payment_from'] or vacancy_sj['payment_to']:
                salaries_sj.append(estimate_salary_sj(vacancy_sj))
    vacancies_sj_processed = len(salaries_sj)
    return vacancies_sj_found, vacancies_sj_processed, salaries_sj


def get_hh_vacancies_statistics(popular_languages):
    """Get and process HeadHunter vacancies for multiple languages."""
    vacancies_language_hh = {}
    for program_language in popular_languages:
        vacancies_hh_found, average_hh_salary, vacancies_hh_processed, vacancies_hh, salaries_hh = get_hh_vacancies(program_language)
        try:
            average_hh_salary = sum(salaries_hh) // len(salaries_hh)
        except ZeroDivisionError:
            average_hh_salary = 0
        salary_hh_statistics = {
            'vacancies_found': vacancies_hh_found,
            'vacancies_processed': vacancies_hh_processed,
            'average_salary': average_hh_salary,
        }
        vacancies_language_hh[program_language] = salary_hh_statistics
    return vacancies_language_hh


def get_sj_vacancies_statistics(popular_languages):
    """Get and process SuperJob vacancies for multiple languages."""
    vacancies_language_sj = {}
    for program_language_sj in popular_languages:
        vacancies_sj_found, average_sj_salary, vacancies_sj_processed, vacancies_sj, salaries_sj = get_sj_vacancies(program_language_sj)
        try:
            average_sj_salary = sum(salaries_sj) // len(salaries_sj)
        except ZeroDivisionError:
            average_sj_salary = 0
        salary_sj_statistics = {
            'vacancies_found': vacancies_sj_found,
            'vacancies_processed': vacancies_sj_processed,
            'average_salary': average_sj_salary,
        }
        vacancies_language_sj[program_language_sj] = salary_sj_statistics
    return vacancies_language_sj


def main():
    load_dotenv(find_dotenv())
    popular_languages = ['C', 'C++', 'C#', 'Java', 'JavaScript', 'Python', 'Ruby', 'Rust']
    title_hh = 'HEADHUNTER (Moscow)'
    title_sj = 'SUPERJOB (Moscow)'

    vacancies_language_hh = get_hh_vacancies_statistics(popular_languages)
    print(create_table(vacancies_language_hh, title_hh))

    vacancies_language_sj = get_sj_vacancies_statistics(popular_languages)
    print(create_table(vacancies_language_sj, title_sj))


if __name__ == '__main__':
    main()
