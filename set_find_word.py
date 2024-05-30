# Поиск слова в описании вакансии включено/отключено (True/False)
find_description: bool = True

# Список специализаций (профессиональных ролей). Если не хотите ничего задавать, оставьте пустым (professional_role =
# [])
# professional_role = []
professional_role: list[int] = [10, 156, 150, 164, 163, 157, 134]

# Задание региона поиска вакансии на hh.ru
# Россия - 113, Москва - 1, Санкт-Петербург - 2
# area = 113
area: int = 2


# Задание списка слов для поиска в названии вакансии и в описании вакансии
# words_find_lst = ['Продакт', 'дата', 'маркетинг', 'BI', 'Аналитик']
# words_find_lst = ['Chef', 'kosmos']
# words_find_lst = ['kosmos']
# words_find_lst = ['Продакт']
# words_find_lst = ['дата']
# words_find_lst = ['дата', 'Аналитик']
words_find_lst: list[str] = ['дата', 'Продакт']
