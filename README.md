# Job Salary Estimator

## Description

Job Salary Estimator is a Python script designed to fetch, analyze, and display salary information for programming job vacancies from platforms such as HeadHunter and SuperJob. It estimates an average salary for popular programming languages based on the fetched vacancies and presents the results in a clear, tabular format.

## Features

- Fetches job vacancies related to popular programming languages.
- Estimates an average salary based on the provided salary ranges in the vacancies.
- Handles different salary providing strategies such as only lower limit, only upper limit, or both.
- Displays the results in a clear table in the console.

## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/StableBig/hhsj_salary.git
```

Navigate to the project directory:

```bash
cd hhsj_salary
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Setup your environment variables in a `.env` file. You will need API keys for the platforms you intend to fetch data from, like SuperJob.

```bash
SUPERJOB_KEY=your_superjob_key
```

Run the script:

```bash
python main.py
```

The script will fetch job vacancies, estimate the salaries, and display the result in tables.
