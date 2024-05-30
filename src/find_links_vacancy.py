import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import re
import json
import urllib.parse


def get_links(arg_dic: dict) -> list:
    """
    Функция поиска ссылок на вакасии по поисковому слову.
    Поиск происходит по вхождению слова в названии вакансии и(или) в описании вакансии.
    :param arg_dic: dict (словарь аргументов строки url)
    :return: links_lst: list (список ссылок на вакансии)
    """
    ua = fake_useragent.UserAgent()
    url_str = f'https://hh.ru/search/vacancy?L_save_area=true&'
    query_arg = urllib.parse.urlencode(arg_dic, doseq=True)
    url_str += query_arg

    # Получение количества страниц
    # url_str = f'{url_str}&page=1'
    print(f'Получение количества страниц по запросу {arg_dic["text"]} по ссылке\n'
          f'{url_str}')
    response = requests.get(url=url_str, headers={"user-agent": ua.random})
    if response.status_code != 200:
        print(f'Ошибка входа на 0 страницу. Ответ сервера={response.status_code}')
        return []
    soup = BeautifulSoup(response.content, 'lxml')
    try:
        page_count: int = (
            int(soup.find('div', attrs={'class': 'pager'})
                .find_all('span', recursive=False)[-1]
                .find("a")
                .find("span").text)
        )
        print(f'Количество страниц cо списками вакансий для поискового слова {arg_dic["text"]} = {page_count}')
    except Exception as err:
        print(f'Ошибка={err}')
        print(f'Поиск {arg_dic["text"]}. Ничего не найдено. Попробуйте изменить поисковый запрос.')
        return []

    links_lst = list()
    page = 0
    delay = 0  # Задержка при ошибках до следующего запроса (увеличивается при ошибках)
    # for page in range(page_count):
    while page < page_count:
        try:
            response = requests.get(url=f'{url_str}&page={page}', headers={"user-agent": ua.random})
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'lxml')
            tmp_link_lst = list()
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    continue  # пустой тег href
                if '.ru/vacancy/' in href:
                    result = re.sub(r'https://.*?hh.ru', 'https://hh.ru', href.split("?")[0])
                    # tmp_link_lst.add(href.split("?")[0])
                    tmp_link_lst.append(result)
            print(f'Обработана страница = {page + 1} из {page_count}, '
                  f'найдено {len(tmp_link_lst)} ссылок на вакансии по запросу = {arg_dic["text"]}')
            if len(tmp_link_lst) != 0:
                links_lst += tmp_link_lst  # Объединяем списки
                delay = 0  # Обнуляем задержку т.к. нет ошибки
                page += 1
            else:
                delay += 10  # Увеличиваем задержку т.к. появилась ошибка
                time.sleep(delay)  # Задержка при ошибке
                continue

        except Exception as err:
            print(f"Ошибка={err}")
        time.sleep(2)

        # break
    return links_lst


def run(settings_args: dict) -> list:
    """
    Функция разделяет запросы отдельно по каждому поисковому слову.
    Объединяет полученные ссылки на вакансии и возвращает в виде словаря
    :param settings_args: dict (словарь аргументов строки url и поисковые слова)
    :return: list: (словарь со ссылками на вакансии)
    """
    links_vacancy_lst = list()  # Общий список ссылок на вакансии

    # Перебор поисковых слов
    for word in settings_args["text"]:
        query_dic = settings_args.copy()
        query_dic["text"] = word
        words_vacancy_lst: list = get_links(query_dic)
        links_vacancy_lst += words_vacancy_lst

    print(f'Общее количество ссылок на вакансии: {len(links_vacancy_lst)} по поисковым словам: {settings_args["text"]}')
    links_vacancy_lst = list(set(links_vacancy_lst))  # Оставляем только уникальные значения
    print(f'Количество ссылок на вакансий после очистки от дубликатов {len(links_vacancy_lst)} '
          f'по поисковым словам: {settings_args["text"]}')
    print(links_vacancy_lst)

    return links_vacancy_lst


if __name__ == "__main__":
    file_path = r'../settings.json'  # Указываем путь к JSON файлу настроек

    # Открываем файл и загружаем его содержимое в словарь
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # print(data)  # Выводим содержимое словаря

    links_vacancy_lst: list = run(data)

    print(links_vacancy_lst)
