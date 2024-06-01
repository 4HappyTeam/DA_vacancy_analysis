import time
import requests
import fake_useragent
from bs4 import BeautifulSoup
import pandas as pd
import json

from src import find_links_vacancy as flv


def get_vacancy(link: str) -> dict:
    """
    Функция по полученной ссылке вакансии производит обработку данных на странице
    :param link: str
    :return: vacancy_dic: dict
    """
    vacancy_dic = {'id': int(link.split('/')[-1])}
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return vacancy_dic
    soup = BeautifulSoup(data.content, "lxml")
    try:
        vacancy_dic['date'] = soup.find(
            'p', attrs={"class": "vacancy-creation-time-redesigned"}
        ).text
    except:
        vacancy_dic['date'] = ""
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
    # try:
    #     vacancy_dic['description'] = soup.find(
    #         'div', attrs={"class": "vacancy-section"}
    #     ).text.replace('\n', '').strip()
    # except:
    #     vacancy_dic['description'] = ""
    # try:
    #     vacancy_dic['description'] = soup.find(
    #         'div', attrs={"class": "g-user-content", "data-qa": "vacancy-description"}
    #     ).text.replace('\n', '').strip()
    # except:
    #     vacancy_dic['description'] = ""
    try:
        vacancy_dic['description'] = soup.find(
            'div', attrs={"data-qa": "vacancy-description"}
        ).text.replace('\n', '').strip()
    except:
        vacancy_dic['description'] = ""

    return vacancy_dic


def main(arg_dic: dict):
    """
    Функция создает csv файл с вакансиями. Имя файла собирается из параметров запроса поиска.
    :param arg_dic: dict (Аргументы параметров запроса поиска, задаются в settings.json)
    """
    links_vacancy_lst = flv.run(arg_dic)  # Список ссылок на вакансии

    # Задание колонок
    columns = ['id', 'date', 'name', 'company', 'salary', 'experience', 'schedule', 'schedule_dop', 'key',
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
    file_name = ''
    for a in arg_dic["area"]:
        file_name += f'{a}_'
    for word in arg_dic["text"]:
        file_name += f'_{word}'
    if len(arg_dic["professional_role"]) != 0:
        for i in arg_dic["professional_role"]:
            file_name += f'_{i}'
    for word in arg_dic["search_field"]:
        file_name += f'_{word}'

    df.to_csv(f'{file_name}.csv', sep=';', index=False)
    print(f'Файл сохранен: {file_name}.csv')


if __name__ == "__main__":

    # file_path = r'settings_Аналитик_msk.json'  # Указываем путь к JSON файлу настроек
    file_path = r'settings.json'  # Указываем путь к JSON файлу настроек

    # Открываем файл и загружаем его содержимое в словарь
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # print(data)  # Выводим содержимое словаря

    main(data)
