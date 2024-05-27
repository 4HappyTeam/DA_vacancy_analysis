import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json


def get_links(world):
    ua = fake_useragent.UserAgent()

    # Получение количества страниц
    response = requests.get(
        url=f'https://hh.ru/search/vacancy?text={world}&area=1&page=1',
        headers={"user-agent": ua.random}
    )
    if response.status_code != 200:
        return
    soup = BeautifulSoup(response.content, 'lxml')
    try:
        # page_count: int = (
        #     int(soup.find('div', attrs={'class': 'pager'})
        #         .find_all('span', recursive=False)[-1]
        #         .find("a")
        #         .find("span").text)
        # )
        page_count: int = (
            int(soup.find('div', class_='pager')
                .find_all('span', recursive=False)[-1]
                .find("a")
                .find("span").text)
        )
        print(f'Количество страниц cо списками вакансий = {page_count}')
    except:
        return

    links_lst = list()
    links_dic = dict()
    for page in range(page_count):
        # print(f'Обрабатывается слово = {text}, страница = {page}')
        try:
            response = requests.get(
                url=f'https://hh.ru/search/vacancy?text={world}&salary=&ored_clusters=true&area=1&page={page}',
                headers={"user-agent": ua.random}
            )
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'lxml')
            # for a in soup.find_all('a', class_='bloko-link'):
            for a in soup.find_all('a', attrs={'class': 'bloko-link', 'target': '_blank'}):
                link = f'{a.get("href").split("?")[0]}'
                # link = f'{a.get("href")}'
                text = a.getText()
                # links_lst.append(link)
                links_dic[link] = text
                # if '.ru/vacancy/' in link:
                #     links_lst.append(link)
        except Exception as err:
            print(f"{err}")
        time.sleep(1)
        break
    print(links_lst)
    print(links_dic)
    print(f'Список {world} = {len(links_lst)}')
    print(f'Словарь {world} = {len(links_dic)}')


if __name__ == "__main__":
    # worlds_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
    # worlds_find_lst = ['Продакт', 'продакт', 'ПРОДАКТ']  # Проверка на чувствительность к регистру
    worlds_find_lst = ['Продакт']  # Проверка на чувствительность к регистру
    for world in worlds_find_lst:
        get_links(world)
