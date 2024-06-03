import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt


files_lst = glob.glob('*.csv')

df = pd.DataFrame()
for f in files_lst:
    tmp_df = pd.read_csv(f, sep=';', encoding='utf-8')
    df = pd.concat([df, tmp_df], axis=0)

# Удаляем дублирующиеся строки
df = df.drop_duplicates()


# Преобразование ключевых навыков key в словарь с навыками в той же колонке
def str_to_lst(text):
    if text != '[]':
        text = text.strip("[]")  # Удаляем скобки "[" и "]" из строки

        # Разделяем строку по запятым и удаляем лишние пробелы
        list_of_strings = text.split(",")
        list_of_strings = [s.replace('\xa0', ' ').strip() for s in list_of_strings]
        return list_of_strings
    else:
        return []


df['key'] = df.key.apply(lambda x: str_to_lst(x))

# Создаем пустой словарь
key_dic = {}

# Перебираем списки из колонки key
for key_lst in df.key:
    # Перебираем элементы списка
    for item in key_lst:
        # Если элемент уже есть в словаре, увеличиваем его значение на 1
        if item in key_dic:
            key_dic[item] += 1
        # Если элемента нет в словаре, добавляем его как ключ со значением 1
        else:
            key_dic[item] = 1

df_key = (
    pd.DataFrame([key_dic]).T
    .sort_values(by=0, ascending=False)
    .reset_index()
    .rename(columns={0: 'count', 'index': 'key_skills'})
)

sns.set_theme(rc={'figure.figsize': (10, 5)})

# Создаем горизонтальный график столбцов с помощью Seaborn
sns.barplot(x='count', y='key_skills', data=df_key.head(15), color='skyblue')

# Добавляем значения на столбцах
for index, value in enumerate(df_key['count'].head(15)):
    plt.text(value, index, str(value), ha='left', va='center')

# Настройка заголовка графика
plt.title('Топ требуемых работодателями ключевых навыков')
plt.ylabel('Ключевые навыки', fontsize=15)  # Установка размера шрифта подписи оси Y
# Настройка отступов слева и справа
plt.subplots_adjust(left=0.4, right=0.9)  # Установка отступов слева и справа
# Сохраняем график в файл изображения
plt.savefig('top_key_skills.png')

# # Отображение графика
# plt.show()
