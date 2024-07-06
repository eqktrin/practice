import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import sqlite3
import urllib.parse



def get_vacancy_links(keyword, area=None, salary=None, experience=None):
    ua = fake_useragent.UserAgent()
    headers = {"User-Agent": ua.random}
    params = {
        "text": keyword,
        "area": area if area else 1,
        "salary": salary,
        "experience": experience
    }
    query = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items() if v)
    url = f"https://hh.ru/search/vacancy?{query}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml")
    vacancy_links = [urllib.parse.urljoin("https://hh.ru", a["href"].split('?')[0])
                     for a in soup.find_all("a", attrs={"class": "bloko-link"})
                     if "/vacancy/" in a["href"]]

    return vacancy_links



def get_vacancy_info(link):
    ua = fake_useragent.UserAgent()
    headers = {"User-Agent": ua.random}

    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {}

    soup = BeautifulSoup(response.content, "lxml")
    title_element = soup.find("h1", attrs={"data-qa": "vacancy-title"})
    company_element = soup.find("a", attrs={"data-qa": "vacancy-company-name"})
    location_element = soup.find("p", attrs={"data-qa": "vacancy-view-location"})

    vacancy_info = {
        'title': title_element.text.strip() if title_element else 'Не указано',
        'company': company_element.text.strip() if company_element else 'Не указано',
        'location': location_element.text.strip() if location_element else 'Не указано'
    }

    return vacancy_info



def main():
    conn = sqlite3.connect('vacancy.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT
    )
    ''')

    while True:
        keyword = input("Введите ключевое слово для поиска вакансий или 'выход' для завершения: ")
        if keyword.lower() == 'выход':
            break


        cursor.execute('DELETE FROM vacancies')
        conn.commit()

        vacancy_links = get_vacancy_links(keyword)
        for link in vacancy_links:
            vacancy_info = get_vacancy_info(link)
            if vacancy_info:
                cursor.execute('''
                INSERT INTO vacancies (title, company, location) 
                VALUES (:title, :company, :location)
                ''', vacancy_info)
                conn.commit()
            time.sleep(1)

    conn.close()


if __name__ == "__main__":
    main()
