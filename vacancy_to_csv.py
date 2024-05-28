import time
import requests
import fake_useragent
from bs4 import BeautifulSoup
import pandas as pd

from src import find_links_vacancy as flv
import set_find_world as set


def get_vacancy(link: str) -> dict:
    """
    Функция по полученной ссылке вакансии производит обработку данных на странице
    :param link: str
    :return: vacancy_dic: dict
    """
    vacancy_dic = {'link': link, 'id': int(link.split('/')[-1])}
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return vacancy_dic
    soup = BeautifulSoup(data.content, "lxml")
    try:
        vacancy_dic['employer'] = soup.find(
            'h1', attrs={"data-qa": "vacancy-title", "class": "bloko-header-section-1"}
        ).text
    except:
        vacancy_dic['employer'] = ""
    try:
        vacancy_dic['name'] = soup.find('span', attrs={"class": "vacancy-company-name"}).text
    except:
        vacancy_dic['name'] = ""
    try:
        vacancy_dic['salary'] = soup.find('span', attrs={"data-qa": "vacancy-salary-compensation-type-net"}).text
    except:
        vacancy_dic['salary'] = ""
    try:
        vacancy_dic['experience'] = soup.find('p', attrs={"class": "vacancy-description-list-item"}).text
    except:
        vacancy_dic['experience'] = ""
    try:
        vacancy_dic['schedule'] = soup.find(
            'p', attrs={"class": "vacancy-description-list-item", "data-qa": "vacancy-view-employment-mode"}
        ).text
    except:
        vacancy_dic['schedule'] = ""
    try:
        vacancy_dic['schedule_dop'] = soup.find(
            'p', attrs={"class": "vacancy-description-list-item", "data-qa": "vacancy-view-accept-temporary"}
        ).text
    except:
        vacancy_dic['schedule_dop'] = ""
    try:
        tmp_lst = []
        for tag in soup.find_all('li', attrs={"data-qa": "skills-element"}):
            tmp_lst.append(tag.text)
        vacancy_dic['key'] = tmp_lst
    except:
        vacancy_dic['key'] = []
    try:
        vacancy_dic['description'] = soup.find(
            'div', attrs={"class": "vacancy-section"}
        ).text.replace('\n', '').strip()
    except:
        vacancy_dic['description'] = ""
    return vacancy_dic


def run(worlds_find_lst: list[str], area=113):
    """
    Функция администратор
    :param worlds_find_lst: list (слова для поиска: задаются в set_find_world.py)
    :param area: int (регион: задается в set_find_world.py)
    """
    links_vacancy_lst = []  # Общий список ссылок на вакансии
    for world in worlds_find_lst:  # Перебор поисковых слов
        links_vacancy_lst += flv.get_links(world, area)  # Добавление списка
    print(f'Всего найдено вакансий {len(links_vacancy_lst)} по словам: {worlds_find_lst}')

    columns = ['link', 'id', 'employer', 'name', 'salary', 'experience', 'schedule', 'schedule_dop', 'key',
               'description']
    df = pd.DataFrame(columns=columns)
    cnt = 0
    delay = 0  # Задержка при ошибках до следующего запроса (увеличивается при ошибках)
    # while cnt < 7:
    while cnt < len(links_vacancy_lst):
        print(f'Обрабатывается вакансия {cnt+1} из {len(links_vacancy_lst)}')
        vacancy_dic = get_vacancy(links_vacancy_lst[cnt])
        if vacancy_dic['employer'] != "":
            df = pd.concat([df, pd.DataFrame([vacancy_dic])], ignore_index=True)
            delay = 0  # Обнуляем задержку т.к. нет ошибки
            cnt += 1
        else:
            delay += 10  # Увеличиваем задержку т.к. появилась ошибка
            time.sleep(delay)
        time.sleep(1)

    # print(df.to_string(max_rows=7, max_cols=10))
    df.to_csv('vacancy.csv', sep=';')  # index=False,


if __name__ == "__main__":
    run(set.worlds_find_lst, set.area)
