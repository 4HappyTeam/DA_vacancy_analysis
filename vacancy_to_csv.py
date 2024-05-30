import time
import requests
import fake_useragent
from bs4 import BeautifulSoup
import pandas as pd

from src import find_links_vacancy as flv
import set_find_word as setting


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
        vacancy_dic['name'] = soup.find(
            'h1', attrs={"data-qa": "vacancy-title", "class": "bloko-header-section-1"}
        ).text
    except:
        vacancy_dic['name'] = ""
    try:
        vacancy_dic['company'] = soup.find('span', attrs={"class": "vacancy-company-name"}).text
    except:
        vacancy_dic['company'] = ""
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


def main(words_find_lst: list[str], area: int, professional_role: list[int], find_description: bool):
    """
    Функция создает csv файл с вакансиями. Имя файла собирается из параметров запроса поиска.
    :param find_description: bool (включение/выключение для поиска поля описания, задается в set_find_word.py)
    :param professional_role: list (список ролей, задается в set_find_word.py)
    :param words_find_lst: list (слова для поиска, задаются в set_find_word.py)
    :param area: int (регион, задается в set_find_word.py)
    """
    links_vacancy_lst = list()  # Общий список ссылок на вакансии
    for word in words_find_lst:  # Перебор поисковых слов
        links_vacancy_lst += flv.get_links(word, area, professional_role, find_description)  # Добавление списка
    print(f'Всего найдено вакансий {len(links_vacancy_lst)} по словам: {words_find_lst}')
    links_vacancy_lst = list(set(links_vacancy_lst))  # Оставляем только уникальные значения
    print(f'Всего найдено вакансий после очистки от дубликатов {len(links_vacancy_lst)} по словам: {words_find_lst}')

    # Задание колонок
    columns = ['link', 'id', 'name', 'company', 'salary', 'experience', 'schedule', 'schedule_dop', 'key',
               'description']
    df = pd.DataFrame(columns=columns)  # DF с вакансиями
    cnt = 0  # Счетчик перебранных вакансий
    delay = 0  # Задержка при ошибках до следующего запроса (увеличивается при ошибках)
    # while cnt < 7:
    while cnt < len(links_vacancy_lst):
        print(f'Обрабатывается вакансия {cnt+1} из {len(links_vacancy_lst)}')
        vacancy_dic = get_vacancy(links_vacancy_lst[cnt])
        if vacancy_dic['name'] != "":
            df = pd.concat([df, pd.DataFrame([vacancy_dic])], ignore_index=True)
            delay = 0  # Обнуляем задержку т.к. нет ошибки
            cnt += 1
        else:
            delay += 10  # Увеличиваем задержку т.к. появилась ошибка
            time.sleep(delay)
        time.sleep(1)  # Глобальная задержка

    # print(df.to_string(max_rows=7, max_cols=10))
    # Сборка имени файла
    file_name = f'{area}'
    for word in words_find_lst:
        file_name += f'_{word}'
    if len(professional_role) != 0:
        for i in professional_role:
            file_name += f'_{i}'
    if find_description:
        file_name += f'_description'
    df.to_csv(f'{file_name}.csv', sep=';')  # index=False,


if __name__ == "__main__":
    main(setting.words_find_lst, setting.area, setting.professional_role, setting.find_description)
