import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import sqlite3
import urllib.parse


def get_resume_links(keyword, area=None, salary=None, experience=None):
    ua = fake_useragent.UserAgent()
    headers = {"User-Agent": ua.random}
    params = {
        "text": keyword,
        "area": area if area else 1,
        "salary": salary,
        "experience": experience
    }
    query = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items() if v)
    url = f"https://hh.ru/search/resume?{query}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml")
    resume_links = [urllib.parse.urljoin("https://hh.ru", a["href"].split('?')[0])
                    for a in soup.find_all("a", attrs={"data-qa": "resume-serp__resume-title"})
                    if "/resume/" in a["href"]]

    return resume_links


def get_resume_info(link):
    ua = fake_useragent.UserAgent()
    headers = {"User-Agent": ua.random}

    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {}

    soup = BeautifulSoup(response.content, "lxml")
    name_element = soup.find(attrs={"class": "resume-block__title-text"})
    desired_salary_element = soup.find(attrs={"class": "resume-block__salary"})
    experience_element = soup.find(attrs={'class': 'resume-block__title-text_sub'})
    experience_list = [exp.text.strip() for exp in experience_element]

    resume_info = {
        'name': name_element.text.strip() if name_element else 'Не указано',
        'desired_salary': desired_salary_element.text.strip() if desired_salary_element else 'Не указано',
        'experience': ' '.join(experience_list) if experience_list else 'Не указано'
    }

    return resume_info




def main():
    conn = sqlite3.connect('resume.db')
    cursor = conn.cursor()


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        desired_salary TEXT,
        experience TEXT
    )
    ''')

    while True:
        keyword = input("Введите ключевое слово для поиска резюме или 'выход' для завершения: ")
        if keyword.lower() == 'выход':
            break


        cursor.execute('DELETE FROM resumes')
        conn.commit()

        resume_links = get_resume_links(keyword)
        for link in resume_links:
            resume_info = get_resume_info(link)
            if resume_info:
                cursor.execute('''
                INSERT INTO resumes (name, desired_salary, experience) 
                VALUES (:name, :desired_salary, :experience)
                ''', resume_info)
                conn.commit()
            time.sleep(1)

    conn.close()

if __name__ == "__main__":
    main()
