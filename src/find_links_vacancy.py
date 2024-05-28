import requests
import fake_useragent
from bs4 import BeautifulSoup
import time


def get_links(world='kosmos', area=113) -> list:
    """
    Функция поиска ссылок на вакасии по поисковому слову.
    Поиск происходит по вхождению слова в названии вакансии и(или) в описании вакансии.
    :param world: string (слово для поиска)
    :param area: int (регион: Россия - 113, Москва - 1, Санкт-Петербург - 2)
    :return: list (список ссылок на вакансии)
    """
    ua = fake_useragent.UserAgent()
    url_str = (f'https://hh.ru/search/vacancy?'
               f'L_save_area=true'
               f'&search_field=name'
               f'&search_field=description'
               f'&excluded_text='
               f'&items_on_page=20'
               f'&text={world}'
               f'&salary='
               f'&ored_clusters=true'
               f'hhtmFrom=vacancy_search_filter'
               f'&area={area}'
               f'&enable_snippets=false'
               f'&experience=doesNotMatter'
               f'&order_by=publication_time')

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
        print(f'Количество страниц cо списками вакансий для поискового слова {world} = {page_count}')
    except Exception as err:
        print(f'Ошибка={err}')
        return []

    links_lst = list()
    for page in range(page_count):
        # print(f'Обрабатывается слово = {world}, страница = {page}')
        try:
            response = requests.get(url=f'{url_str}&page={page}', headers={"user-agent": ua.random})
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'lxml')
            tmp_link_list = []
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    continue  # пустой тег href
                if '.ru/vacancy/' in href:
                    tmp_link_list.append(href.split("?")[0])
            print(f'Обработана страница = {page} найдено {len(tmp_link_list)} ссылок на вакансии по запросу = {world}')
            links_lst += tmp_link_list
        except Exception as err:
            print(f"Ошибка={err}")
        time.sleep(2)
        # break
    return links_lst


if __name__ == "__main__":
    area = 113  # Россия - 113, Москва - 1, Санкт-Петербург - 2
    # worlds_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
    worlds_find_lst = ['Chef', 'kosmos']
    # worlds_find_lst = ['Продакт']
    links_vacancy_lst = []  # Общий список ссылок на вакансии
    for world in worlds_find_lst:
        world_vacancy_lst = get_links(world, area)
        links_vacancy_lst += world_vacancy_lst
        print(world_vacancy_lst)
        print(f'Список {world} = {len(world_vacancy_lst)}')

    print(f'Общий список по поисковым словам {worlds_find_lst} = {len(links_vacancy_lst)}')
