import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import re


def get_links(word: str, area: int, professional_role: list, find_description: bool) -> list:
    """
    Функция поиска ссылок на вакасии по поисковому слову.
    Поиск происходит по вхождению слова в названии вакансии и(или) в описании вакансии.
    :param professional_role: list (список профессиональных ролей)
    :param find_description: bool (Поиск по полю описания)
    :param word: string (слово для поиска)
    :param area: int (регион: Россия - 113, Москва - 1, Санкт-Петербург - 2)
    :return: links_lst: set (множество ссылок на вакансии)
    """
    ua = fake_useragent.UserAgent()
    url_str = (f'https://hh.ru/search/vacancy?'
               f'L_save_area=true'
               f'&search_field=name'
               # f'&search_field=description'  # Можно закомментировать, чтобы искать слова только в названии вакансии
               # f'&excluded_text=учитель%2Cрекрутер%2Cрежиссер%2Cкрупье%2Cсмотритель%2Cврач%2Cкладовщик'
               f'&items_on_page=20'
               f'&text={word}'
               f'&salary='
               f'&ored_clusters=true'
               f'&hhtmFrom=vacancy_search_filter'
               f'&area={area}'
               f'&enable_snippets=false'
               f'&experience=doesNotMatter'
               f'&order_by=publication_time')

    # Добавление профессиональных ролей
    professional_role_str = ''
    if len(professional_role) != 0:
        for i in professional_role:
            professional_role_str += f'&professional_role={i}'
        url_str += professional_role_str

    # Добавление поиска в поле описания
    if find_description:
        url_str += '&search_field=description'

    # print(url_str)
    # return

    # Получение количества страниц
    response = requests.get(url=f'{url_str}&page=0', headers={"user-agent": ua.random})
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
        print(f'Количество страниц cо списками вакансий для поискового слова {word} = {page_count}')
    except Exception as err:
        print(f'Ошибка={err}')
        print(f'Поиск {word}. Ничего не найдено. Попробуйте изменить поисковый запрос.')
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
                  f'найдено {len(tmp_link_lst)} ссылок на вакансии по запросу = {word}')
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


if __name__ == "__main__":
    # Ниже отладочный отладочный код, для запуска из этого файла.

    # Поиск слова в описании вакансии включено/отключено (True/False)
    find_description = True

    # Список спациализаций (профессиональных ролей).
    # professional_role = []
    professional_role = [10, 156, 150, 164, 163, 157, 134]

    # Регион поиска
    area = 113  # Россия - 113, Москва - 1, Санкт-Петербург - 2

    # Слова для поиска
    # words_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
    # words_find_lst = ['Chef', 'kosmos']
    words_find_lst = ['дата', 'Продакт']
    # words_find_lst = ['дата']

    links_vacancy_lst = list()  # Общий список ссылок на вакансии
    for word in words_find_lst:
        words_vacancy_lst: list = get_links(word, area, professional_role, find_description)
        links_vacancy_lst += words_vacancy_lst
        print(f'Список {word} = {len(words_vacancy_lst)}')

    links_vacancy_lst = list(set(links_vacancy_lst))  # Оставляем только уникальные значения
    print(f'Общий список по поисковым словам {words_find_lst} = {len(links_vacancy_lst)}')
    print(links_vacancy_lst)
