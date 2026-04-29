import datetime
import json
from model import Expense
from typing import Optional

records = []
filter_date_reverse = None
file = "history.json"


def add_date() -> datetime.datetime:
    while True:
        try:
            new_date = input("Введите дату в формате дд.мм.гггг: ").strip()
            new_date = datetime.datetime.strptime(new_date, "%d.%m.%Y")
            return new_date
        except ValueError:
            print("Ошибка. Недопустимое значение.\n")


def add_amount() -> float:
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


def add_category() -> str:
    while True:
        category = input("Введите название категории: ").strip().title()
        if category == "":
            print("Ошибка. Пустая строка.")
            continue
        return category


def add_new_record():
    print("\nДобавление новой записи.")
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


def sort_records_date(current_list: list) -> list:
    global filter_date_reverse
    if filter_date_reverse is None:
        choice_filter_date()
    return sorted(current_list, key=Expense.get_date, reverse=filter_date_reverse)


def sort_records_category(current_list: list) -> list:
    return sorted(current_list, key=Expense.get_category)


def show_history():
    global records
    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return
    records_sorted = sort_records_date(records)
    print("\nВыберите способ сортировки: ")
    print("1. По датам")
    print("2. По категориям")
    print("Любая другая клавиша для возврата в меню.")
    choice = input("> ").strip()
    if choice == "1":
        show_list = records_sorted
    elif choice == "2":
        show_list = sort_records_category(records)
    else:
        print("Неизвестная команда. Возврат в меню.")
        return
    for record in show_list:
        print("===")
        record.show_record()
        print("===")


def period():
    print("\nУкажите начало периода.", end=" ")
    begin = add_date()
    print("\nУкажите конец периода.", end=" ")
    end = add_date()
    delta = end - begin
    if delta.days < 0:
        print("Ошибка. Неверно указаны начало и конец периода.")
        return None
    return begin, end


def find_records_date(begin: datetime.datetime, end: Optional[datetime.datetime]):
    global records
    records_sorted = sort_records_date(records)
    current_list = []

    if end is None:
        end = begin

    for record in records_sorted:
        if record.date >= begin and record.date <= end:
            print("===")
            record.show_record()
            print("===")
            current_list.append(record)

    if current_list:
        return current_list
    else:
        print("Записи не найдены.")
        return None


def find_record_category(category: str):
    global records
    records_sorted = sort_records_date(records)
    current_list = []

    for record in records_sorted:
        if record.category.lower() == category.lower():
            print("===")
            record.show_record()
            print("===")
            current_list.append(record)

    if current_list:
        return current_list
    else:
        print(f"Записи в категории '{category}' не найдены.")
        return None


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
        period_result = period()
        if period_result is None:
            return
        begin, end = period_result
        find_records_date(begin, end)
    elif choice == "3":
        category = add_category()
        find_record_category(category)
    else:
        print("Неизвестная команда. Возврат в меню.")
        return


def delete(deletion_list: list):
    global records
    for record in deletion_list:
        if record in records:
            records.remove(record)


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
        deletion_list = find_records_date(date, None)
    elif choice == "2":
        period_result = period()
        if period_result is None:
            return
        begin, end = period_result
        deletion_list = find_records_date(begin, end)
    elif choice == "3":
        category = add_category()
        deletion_list = find_record_category(category)
    elif choice == "4":
        deletion_list = records.copy()
        print("Выбраны все сохранённые записи. ", end="")
    else:
        print("Неизвестная команда. Возврат в меню.")
        return

    if not deletion_list:
        return

    choice_del = input("Удалить? (да / нет) ").strip().lower()
    if choice_del == "да":
        delete(deletion_list)
        print("Записи были удалены.")
    else:
        print("Отмена.")


def find_amount_period():
    period_result = period()
    if period_result is None:
        return
    begin, end = period_result
    records_period = find_records_date(begin, end)
    if records_period is None:
        return
    total_amount = sum(record.amount for record in records_period)
    print("\nСумма трат за период:", total_amount)


def load_records():
    global records
    global file
    try:
        with open(file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка. Файл {file} не найден.")
        return
    if not loaded_data:
        print("Нет сохранённых записей.")
        return
    for record in loaded_data:
        amount = record["Amount"]
        category = record["Category"]
        date_str = record["Date"]
        try:
            date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            print("Ошибка! У записи неверно указана дата:", date_str)
            print("Запись не будет загружена.")
            continue
        new_record = Expense(amount, category, date_obj)
        if new_record not in records:
            records.append(new_record)
    print("Доступные записи были загружены!")


def save_records():
    global records
    global file
    if len(records) == 0:
        print("\nНет сохранённых записей.")
        return
    records_sorted = sort_records_date(records)
    json_list = []
    for record in records_sorted:
        amount = record.amount
        category = record.category
        date_str = datetime.datetime.strftime(record.date, "%d.%m.%Y")
        json_record = {"Amount": amount, "Category": category, "Date": date_str}
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
    print(f"\nЗаписи были успешно сохранены в файл {file}.")


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
        print("8. Завершить работу")
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
            if not was_loaded:
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
