import datetime


class Expense:
    def __init__(self, amount: float, category: str, date: datetime.datetime):
        self.amount = amount
        self.category = category
        self.date = date

    def show_record(self):
        print("Сумма траты: ", self.amount)
        print("Категория: ", self.category)
        print("Дата: ", datetime.datetime.strftime(self.date, "%d.%m.%Y"))

    def get_date(self):
        return self.date

    def get_category(self):
        return self.category
