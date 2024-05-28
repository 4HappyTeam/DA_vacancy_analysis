import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import pandas as pd

import find_links_vacancy as flv


def get_vacancy(link):
    """

    :param link:
    :return:
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
        employer = soup.find(attrs={"class": "resume-block__title-text"}).text
    except:
        employer = ""
    # try:
    #     name = soup.find(attrs={"class": "resume-block__title-text"}).text
    # except:
    #     name = ""
    # try:
    #     salary = (soup.find(attrs={"class": "resume-block__title-text_salary"}).text.replace("\u2009", "").replace(
    #         "\xa0", " "))
    # except:
    #     salary = ""
    # try:
    #     tags = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"}).find_all("span", attrs={
    #         "class": "bloko-tag__section_text"})]
    # except:
    #     tags = []
    # resume = {
    #     "name": name,
    #     "salary": salary,
    #     "tags": tags,
    # }
    return vacancy_dic


def run(worlds_find_lst: list[str], area=113):
    """
    Функция
    :param worlds_find_lst: list (слова для поиска)
    :param area: int (регион: Россия - 113, Москва - 1, Санкт-Петербург - 2)
    :return:
    """
    links_vacancy_lst = []  # Общий список ссылок на вакансии
    for world in worlds_find_lst:
        links_vacancy_lst += flv.get_links(world, area)

    columns = ['link', 'id', 'employer', 'name', 'salary', 'from', 'to', 'experience', 'schedule', 'keys', 'description']
    df = pd.DataFrame(columns=columns)
    for link in links_vacancy_lst:
        vacancy_dic = get_vacancy(link)
        df = pd.concat([df, pd.DataFrame([vacancy_dic])], ignore_index=True)
        print(df)
        break


if __name__ == "__main__":
    area = 113  # Россия - 113, Москва - 1, Санкт-Петербург - 2
    # worlds_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
    # worlds_find_lst = ['Chef', 'kosmos']
    worlds_find_lst = ['kosmos']
    # worlds_find_lst = ['Продакт']

    run(worlds_find_lst, area)
