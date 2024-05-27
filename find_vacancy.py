import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json


def get_links(text):
    ua = fake_useragent.UserAgent()

    # Получение количества страниц
    response = requests.get(
        url=f'https://hh.ru/search/vacancy?text={text}&area=1&page=1',
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
    for page in range(page_count):
        # print(f'Обрабатывается слово = {text}, страница = {page}')
        try:
            response = requests.get(
                url=f'https://hh.ru/search/vacancy?text={text}&area=1&page={page}',
                headers={"user-agent": ua.random}
            )
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'lxml')
            for a in soup.find_all('a', attrs={'class': 'bloko-link'}):
                link = f'{a.attrs["href"].split("?")[0]}'
                # yield f'{a.attrs["href"].split("?")[0]}'
                # links_lst.append(f'{a.attrs["href"].split("?")[0]}')
                if '.ru/vacancy/' in link:
                    links_lst.append(link)
        except Exception as err:
            print(f"{err}")
        time.sleep(1)
        # break
    # print(links_lst)
    print(f'{text} = {len(links_lst)}')







    # res = requests.get(
    #     url=f"https://hh.ru/search/resume?relocation=living_or_relocation&gender=unknown&text={text}&"
    #         f"isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&fromSearchLine=false&search_period=0",
    #     headers={"user-agent": ua.random}
    # )
    # if res.status_code != 200:
    #     return
    # soup = BeautifulSoup(res.content, "lxml")
    # try:
    #     page_count = int(
    #         soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find(
    #             "span").text)
    # except:
    #     return
    # for page in range(page_count):
    #     try:
    #         res = requests.get(
    #             url=f"https://hh.ru/search/resume?relocation=living_or_relocation&gender=unknown&text={text}&"
    #                 f"isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&"
    #                 f"fromSearchLine=false&search_period=0&page={page}",
    #             headers={"user-agent": ua.random}
    #         )
    #         if res.status_code == 200:
    #             soup = BeautifulSoup(res.content, "lxml")
    #             for a in soup.find_all("a", attrs={"class": "resume-search-item__name"}):
    #                 yield f'https://hh.ru{a.attrs["href"].split("?")[0]}'
    #     except Exception as e:
    #         print(f"{e}")
    #     time.sleep(1)
    # print(page_count)


def get_resume(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        name = soup.find(attrs={"class": "resume-block__title-text"}).text
    except:
        name = ""
    try:
        salary = (soup.find(attrs={"class": "resume-block__title-text_salary"}).text.replace("\u2009", "").replace(
            "\xa0", " "))
    except:
        salary = ""
    try:
        tags = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"}).find_all("span", attrs={
            "class": "bloko-tag__section_text"})]
    except:
        tags = []
    resume = {
        "name": name,
        "salary": salary,
        "tags": tags,
    }
    return resume


def download_data(tag, filename):
    data = []
    for a in get_links(tag):
        data.append(get_resume(a))
        time.sleep(1)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def read_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def get_skills(data, freq):
    skills = {}
    dataCount = 0
    for d in data:
        if not d:
            continue
        dataCount += 1
        for tag in d.get("tags", []):
            skills[tag] = skills.get(tag, 0) + 1

    skills = {k: v / dataCount for k, v in skills.items() if v / dataCount >= freq}
    skills_sorted = sorted(skills, key=lambda x: skills[x], reverse=True)
    return {skill: skills[skill] for skill in skills_sorted}


if __name__ == "__main__":
    # worlds_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
    worlds_find_lst = ['Продакт', 'продакт', 'ПРОДАКТ']  # Проверка на чувствительность к регистру
    for world in worlds_find_lst:
        get_links(world)

    # for a in get_links('Продакт'):
    #     print(a)

    # data = read_data("frontend.json")
    # print("FRONTEND")
    # for k, v in get_skills(data, 0.1).items():
    #     print(k, v)
    #
    # data = read_data("data.json")
    # print("PYTHON")
    # for k, v in get_skills(data, 0.1).items():
    #     print(k, v)
