# Добавление, просмотр и удаление записей.
# Фильтрация по категории или дате.
# Подсчёт суммы расходов за период.
import datetime
import json
from model import Expense

records = []
filter_date_reverse = None
file = "history.json"


# Принимает от пользователя дату
def add_date():
    while True:
        try:
            new_date = input("Введите дату в формате дд.мм.гггг: ").strip()
            new_date = datetime.datetime.strptime(new_date, "%d.%m.%Y")
            return new_date
        except ValueError:
            print("Ошибка. Недопустимое значение.\n")


# Принимает от пользователя сумму траты и округляет её до двух знаков после запятой
def add_amount():
    while True:
        try:
            amount = float(input("Введите сумму траты: "))
            if amount < 0.01:
                print(f"Ошибка. Значение не может быть меньше 0.01!\n")
                continue

        except ValueError:
            print("Ошибка. Введите числовое значение.\n")
            continue

        return round(amount, 2)


# Принимает от пользователя категорию
def add_category():
    while True:
        category = input("Введите название категории: ").strip().title()
        if category == "":
            print("Ошибка. Пустая строка.")
            continue

        return category


# Добавляет новую запись в виде класса Expense
def add_new_record():

    print("\nДобавление новой записи.")
    amount = None
    date = None

    amount = add_amount()

    date = add_date()

    category = add_category()

    new_record = Expense(amount, category, date)

    print("\nТекущая запись:")
    new_record.show_record()

    choice = input("Сохранить запись? (да / нет) ").strip().lower()

    if choice == "да":
        global records
        records.append(new_record)
        print("Запись сохранена!")
    else:
        print("Отмена.")


# Меняет глобальную настройку фильтрации дат
def choice_filter_date():
    global filter_date_reverse

    while True:
        print("\nВыберите порядок, в котором будут показаны записи:")
        print("1. По актуальности — от новых к старым")
        print("2. По хронологии — от старых к новым")
        choice = input("> ")

        if choice == "1":
            filter_date_reverse = True
        elif choice == "2":
            filter_date_reverse = False
        else:
            print("Ошибка. Неизвестная команда.")
            continue

        return


# Сортирует записи в листе по датам (в указанном порядке)
def sort_records_date(current_list: list):
    global filter_date_reverse

    if filter_date_reverse == None:
        choice_filter_date()

    current_list = sorted(
        current_list, key=Expense.get_date, reverse=filter_date_reverse
    )
    return current_list


# Сортирует записи в листе по категориям (в алфавитном порядке)
def sort_records_category(current_list: list):
    current_list = sorted(current_list, key=Expense.get_category)
    return current_list


# Отображение истории (с фильтрацией по датам и категориям)
def show_history():
    global records

    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return

    records = sort_records_date(records)

    print("\nВыберите способ сортировки: ")
    print("1. По датам")
    print("2. По категориям")
    print("Любая другая клавиша для возврата в меню.")

    choice = input("> ").strip()

    if choice == "1":
        show_list = records
    elif choice == "2":
        show_list = sort_records_category(records)
    else:
        print("Неизвестная команда. Возврат в меню.")
        return

    for record in show_list:
        print("===")
        record.show_record()
        print("===")


# Выбор периода (возвращает значения начала и конца периода)
def period():
    print("\nУкажите начало периода.", end=" ")
    begin = add_date()
    print("\nУкажите конец периода.", end=" ")
    end = add_date()

    delta = end - begin
    if delta.days < 0:
        print("Ошибка. Неверно указаны начало и конец периода.")
        return

    return begin, end


# Выводит и возвращает записи за день или период (выводит сообщение, если записи не найдены)
def find_records_date(begin: datetime.datetime, end: datetime.datetime | None):
    global records

    records = sort_records_date(records)
    current_list = []

    if end == None:
        end = begin

    for record in records:
        if record.date >= begin and record.date <= end:
            print("===")
            record.show_record()
            print("===")
            current_list.append(record)

    if current_list:
        return current_list
    else:
        print("Записи не найдены.")
        return


# Выводит и возвращает записи в указанной категории (выводит сообщение, если записи не найдены)
def find_record_category(category: str):
    global records

    records = sort_records_date(records)
    current_list = []

    for record in records:
        current_category = record.category
        if current_category.lower() == category.lower():
            print("===")
            record.show_record()
            print("===")
            current_list.append(record)

    if current_list:
        return current_list
    else:
        print(f"Записи в категории '{category}' не найдены.")
        return


# Поиск записей
def find_records():
    global records

    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return

    print("\n1. Найти записи по выбранной дате")
    print("2. Найти записи за выбранный период")
    print("3. Найти записи по категории")
    print("Любая другая клавиша для возврата в меню.")

    choice = input("> ")

    if choice == "1":
        date = add_date()
        find_records_date(date, None)
    elif choice == "2":
        begin, end = period()
        find_records_date(begin, end)
    elif choice == "3":
        category = add_category()
        find_record_category(category)
    else:
        print("Неизвестная команда. Возврат в меню.")
        return


# Удаление всех записей в указанном листе из списка записей
def delete(deletion_list: list):
    global records

    old_records = records

    for record in old_records:
        if record in deletion_list:
            records.remove(record)


# Выбор и удаление записей
def remove_records():
    global records

    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return

    print("\n1. Найти и удалить записи по выбранной дате")
    print("2. Найти и удалить записи за выбранный период")
    print("3. Найти и удалить записи по категории")
    print("4. Удалить все записи")
    print("Любая другая клавиша для возврата в меню.")

    choice = input("> ")

    if choice == "1":
        date = add_date()
        deletion_list = find_records_date(date)
    elif choice == "2":
        begin, end = period()
        deletion_list = find_records_date(begin, end)
    elif choice == "3":
        category = input("Введите название категории: ").strip()
        deletion_list = find_record_category(category)
    elif choice == "4":
        deletion_list = records
        print("Выбраны все сохранённые записи. ", end="")
    else:
        print("Неизвестная команда. Возврат в меню.")
        return

    if deletion_list == None:
        return

    choice = input("Удалить? (да / нет) ").strip().lower()
    if choice == "да":
        delete(deletion_list)
        print("Записи были удалены.")
    else:
        print("Отмена.")


# Рассчёт суммы расходов за период
def find_amount_period():
    begin, end = period()

    records_period = find_records_date(begin, end)
    if records_period == None:
        return

    total_amount = 0
    for record in records_period:
        total_amount += record.amount

    print("\nСумма трат за период:", total_amount)


# Загрузка записей из файла
def load_records():
    global records
    global file

    try:
        with open(file, "r", encoding="utf-8") as f:
            load_records = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка. Файл {file} не найден.")
        return

    if not load_records:
        print("Нет сохранённых записей.")
        return

    for record in load_records:
        amount = record["Amount"]
        category = record["Category"]
        date = record["Date"]

        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            print("Ошибка! У записи неверно указана дата:", date)
            print("Запись не будет загружена.")
            continue

        new_record = Expense(amount, category, date)

        if not new_record in records:
            records.append(new_record)

    print("Доступные записи были загружены!")


# Сохранение записей в файл
def save_records():
    global records
    global file

    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return

    records = sort_records_date(records)

    json_list = []

    for record in records:
        amount = record.amount
        category = record.category
        date = datetime.datetime.strftime(record.date, "%d.%m.%Y")
        json_record = {"Amount": amount, "Category": category, "Date": date}
        json_list.append(json_record)

    print(
        f"\nСтарый файл {file} будет полностью перезаписан. Убедитесь, что данные из него были загружены или сохранены."
    )
    choice = input("Сохранить записи? (да / нет) ").strip().lower()
    if choice != "да":
        print("Отмена.")
        return

    with open(file, "w", encoding="utf-8") as f:
        json.dump(json_list, f, indent=4, ensure_ascii=False)

    print(f"\nЗаписи были загружены в файл {file}.")


# Главное меню
def main():
    global file
    was_loaded = False

    print("Ваш трекер расходов~")

    while True:
        print("\nВыберите команду:")
        print("1. Добавить новую запись")
        print("2. Просмотреть историю")
        print("3. Удалить записи")
        print("4. Найти записи по фильтру")
        print("5. Рассчитать сумму расходов за период")
        print(f"6. Загрузить записи из файла {file}")
        print(f"7. Сохранить записи в файл {file}")
        print("8. Завершение работы")

        choice = input("> ").strip()

        if choice == "1":
            add_new_record()
        elif choice == "2":
            show_history()
        elif choice == "3":
            remove_records()
        elif choice == "4":
            find_records()
        elif choice == "5":
            find_amount_period()

        elif choice == "6":
            if was_loaded == False:
                load_records()
                was_loaded = True
            else:
                print(f"Записи из файла {file} уже были загружены.")
        elif choice == "7":
            save_records()

        elif choice == "8":
            print("До новых встреч!")
            break
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()
