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
    """
    Takes a job vacancy dictionary from HeadHunter (vacancy_hh) and returns an
    estimated average salary based on the salary information provided in the vacancy.
    """
    salary_hh = 0
    salary_from_hh = vacancy_hh['salary']['from']
    salary_to_hh = vacancy_hh['salary']['to']
    salary_hh = calculate_avg_salary(salary_from_hh, salary_to_hh)
    return salary_hh


def estimate_salary_sj(vacancy_sj):
    """
    Takes a job vacancy dictionary from SuperJob (vacancy_sj) and returns an
    estimated average salary based on the salary information provided in the vacancy.
    """
    salary_sj = 0
    salary_from_sj = vacancy_sj['payment_from']
    salary_to_sj = vacancy_sj['payment_to']
    salary_sj = calculate_avg_salary(salary_from_sj, salary_to_sj)
    return salary_sj


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


def main():
    load_dotenv(find_dotenv())
    sj_key = os.environ.get('SUPERJOB_KEY')
    popular_languages = ['C', 'C++', 'C#', 'Java', 'JavaScript', 'Python', 'Ruby', 'Rust']
    vacancies_language_hh = {}
    vacancies_hh = []
    salaries_hh = []
    moscow_id = 1
    amount_of_days = 31
    max_pages_hh = 20
    amount_of_vacancies_on_page = 50
    title_hh = 'HEADHUNTER (Moscow)'
    title_sj = 'SUPERJOB (Moscow)'
    headers_hh = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    for program_language in popular_languages:
        vacancies_hh_found = 0
        average_hh_salary = 0
        vacancies_hh_processed = 0
        vacancies_hh.clear()
        salaries_hh.clear()
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
        for page_with_hh_vacancies in vacancies_hh:
            vacancies_records = page_with_hh_vacancies['items']
            vacancies_hh_found = page_with_hh_vacancies['found']
            for vacancy_hh in vacancies_records:
                if vacancy_hh['salary']:
                    salaries_hh.append(estimate_salary_hh(vacancy_hh))
        try:
            average_hh_salary = sum(salaries_hh) // len(salaries_hh)
        except ZeroDivisionError:
            average_hh_salary = 0
        vacancies_hh_processed = len(salaries_hh)
        salary_hh_statistics = {
                'vacancies_found': vacancies_hh_found,
                'vacancies_processed': vacancies_hh_processed,
                'average_salary': average_hh_salary,
            }
        vacancies_language_hh[program_language] = salary_hh_statistics

    print(create_table(vacancies_language_hh, title_hh))

    vacancies_language_sj = {}
    vacancies_sj = []
    salaries_sj = []
    headers_sj = {
        'X-Api-App-Id': sj_key,
    }

    publication_period = 0
    max_number_of_results = 100
    max_pages_sj = 5

    for program_language_sj in popular_languages:
        vacancies_sj_found = 0
        average_sj_salary = 0
        vacancies_sj_processed = 0
        vacancies_sj.clear()
        salaries_sj.clear()
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
        for page_with_sj_vacancies in vacancies_sj:
            vacancies_sj_records = page_with_sj_vacancies['objects']
            vacancies_sj_found = page_with_sj_vacancies['total']
            for vacancy_sj in vacancies_sj_records:
                if vacancy_sj['payment_from'] != 0 or vacancy_sj['payment_to'] != 0:
                    salaries_sj.append(estimate_salary_sj(vacancy_sj))
        try:
            average_sj_salary = sum(salaries_sj) // len(salaries_sj)
        except ZeroDivisionError:
            average_sj_salary = 0
        vacancies_sj_processed = len(salaries_sj)
        salary_sj_statistics = {
            'vacancies_found': vacancies_sj_found,
            'vacancies_processed': vacancies_sj_processed,
            'average_salary': average_sj_salary,
        }
        vacancies_language_sj[program_language_sj] = salary_sj_statistics
    print(create_table(vacancies_language_sj, title_sj))


if __name__ == '__main__':
    main()
